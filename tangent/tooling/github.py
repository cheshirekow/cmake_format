# PYTHON_ARGCOMPLETE_OK
"""
Commandline client for github API
"""

import argparse
import collections
import inspect
import io
import json
import logging
import os
import re
import sys

import requests

logger = logging.getLogger(__name__)


def parse_bool(string):
  if string.lower() in ('y', 'yes', 't', 'true', '1', 'yup', 'yeah', 'yada'):
    return True
  if string.lower() in ('n', 'no', 'f', 'false', '0', 'nope', 'nah', 'nada'):
    return False

  logger.warning("Ambiguous truthiness of string '%s' evalutes to 'FALSE'",
                 string)
  return False


if sys.version_info >= (3, 0, 0):
  VALUE_TYPES = (str, int, float)
else:
  VALUE_TYPES = (str, unicode, int, float)


class Descriptor(object):
  # TODO(josh): consider storing a global construction order among
  # descriptors. This would allow us to iterate over config object descriptors
  # in deterministic (construction) order even in pythons where
  # __dict__.items() does not return objects in declaration order.
  pass


class FieldDescriptor(Descriptor):
  """Implements the descriptor interface to store metadata (default value,
  docstring, and choices) for each configuration variable.
  """

  def __init__(
      self, default_value=None, helptext=None, choices=None, required=False,
      positional=False):
    super(FieldDescriptor, self).__init__()
    self.default_value = default_value
    self.helptext = helptext
    self.choices = choices
    self.required = required
    self.positional = positional
    self.name = "<unnamed>"

  def __get__(self, obj, objtype):
    return getattr(obj, "_" + self.name, self.default_value)

  def __set__(self, obj, value):
    setattr(obj, "_" + self.name, value)

  def __set_name__(self, owner, name):
    # pylint: disable=protected-access
    owner._field_registry.append(self)
    self.name = name

  def consume_value(self, obj, value):
    """Convenience method to consume values directly from the descriptor
    interface."""
    self.__set__(obj, value)

  def has_override(self, obj):
    """Return true if `obj` has an override for this configuration variable."""
    return hasattr(obj, "_" + self.name)

  def add_to_argparse(self, optgroup):
    """Add the config variable as an argument to the command line parser."""
    if self.name == 'additional_commands':
      return

    argname = self.name
    kwargs = {
        "help": self.helptext
    }
    if not self.positional:
      argname = "--" + self.name.replace("_", "-")
      kwargs["required"] = self.required

    if isinstance(self.default_value, bool):
      # NOTE(josh): argparse store_true isn't what we want here because we
      # want to distinguish between "not specified" = "default" and
      # "specified"
      optgroup.add_argument(
          argname, nargs='?',
          default=None, const=(not self.default_value),
          type=parse_bool, **kwargs)
    elif isinstance(self.default_value, VALUE_TYPES):
      optgroup.add_argument(
          argname,
          type=type(self.default_value),
          choices=self.choices, **kwargs)
    elif self.default_value is None:
      # If the value is None then we can't really tell what it's supposed to
      # be. I guess let's assume string in this case.
      optgroup.add_argument(
          argname,
          choices=self.choices, **kwargs)
    # NOTE(josh): argparse behavior is that if the flag is not specified on
    # the command line the value will be None, whereas if it's specified with
    # no arguments then the value will be an empty list. This exactly what we
    # want since we can ignore `None` values.
    elif isinstance(self.default_value, (list, tuple)):
      typearg = None
      if self.default_value:
        typearg = type(self.default_value[0])
      optgroup.add_argument(
          argname,
          nargs='*', type=typearg, **kwargs)


def class_to_cmd(name):
  intermediate = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1-\2', intermediate).lower()


class Command(object):
  """
  Base class making it a little easier to set up a complex argparse tree by
  specifying features of a command as members of a class.
  """
  _field_registry = []

  @classmethod
  def cmdname(cls):
    """
    Return a string command name formulated by de-camael-casing the class
    name.
    """
    return class_to_cmd(cls.__name__)

  @classmethod
  def add_parser(cls, subparsers):
    """
    Add a subparser to the list of subparsers, and then call the classmethod
    to configure that subparser.
    """
    subparser = subparsers.add_parser(cls.cmdname(), help=cls.__doc__)
    for descr in cls._field_registry:
      descr.add_to_argparse(subparser)
    cls.setup_subparser(subparser)

  @classmethod
  def setup_subparser(cls, subparser):
    """
    Configure subparser for this command. Override in subclasses.
    """

  def __init__(self, _config, **kwargs):
    for _, descr in self._field_registry:
      if descr.name in kwargs:
        descr.consume_value(self, kwargs.pop(descr.name))

  def __call__(self, *args, **kwargs):
    raise NotImplementedError('__call__ unimplemented for object of type {}'
                              .format(type(self).__name__))


class ReleaseBase(Command):
  _field_registry = []

  target_commitish = FieldDescriptor(
      "",
      helptext=(
          "Specifies the commitish value that determines where the Git tag is"
          " created from. Can be any branch or commit SHA. Unused if the Git"
          " tag already exists. Default: the repository's default branch"
          " (usually master)."))

  name = FieldDescriptor("", helptext="The name of the release.")
  body = FieldDescriptor("", helptext="Text describing the contents of the tag")
  draft = FieldDescriptor(
      False,
      helptext=(
          "true to create a draft (unpublished) release, false to create a"
          " published one. Default: false"))

  prerelease = FieldDescriptor(
      False,
      helptext=(
          "true to identify the release as a prerelease. false to identify the"
          " release as a full release. Default: false"))

  def get_data(self):
    if self.body.startswith("file://"):
      with io.open(self.body[len("file://"):], "r", encoding="utf-8") as infile:
        body = infile.read()
    else:
      body = self.body

    return {
        "tag_name": self.tag_name,
        "target_commitish": self.target_commitish,
        "name": self.name,
        "body": body,
        "draft": self.draft,
        "prerelease": self.prerelease
    }


class CreateRelease(ReleaseBase):
  """
  :see: https://developer.github.com/v3/repos/releases/#create-a-release
  """

  _field_registry = list(ReleaseBase._field_registry)

  tag_name = FieldDescriptor(
      "", positional=True, helptext="Required. The name of the tag.")

  def __call__(self, http):
    data = self.get_data()
    return http.post("releases")


class EditRelease(ReleaseBase):
  """
  :see: https://developer.github.com/v3/repos/releases/#edit-a-release
  """

  _field_registry = list(ReleaseBase._field_registry)

  tag_name = FieldDescriptor(
      "", helptext="The name of the tag.")

  release_id = FieldDescriptor(
      "", positional=True, helptext="id of the release to edit")

  def __call__(self, http):
    data = self.get_data()
    return http.patch("releases/:release_id")


class Repo(Command):

  _field_registry = []

  repo_slug = FieldDescriptor(
      "", positional=True, helptext="Required. <owner>/<repository>")

  _subcmds = {
      cls.cmdname(): cls for cls in [
          CreateRelease, EditRelease
      ]}

  @classmethod
  def setup_subparser(cls, subparser):
    subsubparser = subparser.add_subparsers(dest="repo_cmd")

    for _, cmd in cls._subcmds.items():
      cmd.add_parser(subsubparser)

  def __call__(self, http, repo_cmd, **kwargs):
    cmdobj = self._subcmds[repo_cmd](None, **kwargs)
    cmdobj(None, **kwargs)


def get_argdict(namespace):
  out = {}
  for key, value in vars(namespace).items():
    if key.startswith("_"):
      continue
    out[key] = value
  return out


def setup_argparser(argparser, cmds):
  subparsers = argparser.add_subparsers(
      dest="command", help="sub-command. See --help")
  for _, cmd in cmds.items():
    cmd.add_parser(subparsers)


def main():
  logging.basicConfig(level=logging.INFO)
  argparser = argparse.ArgumentParser(description=__doc__)
  cmds = {
      cls.cmdname(): cls for cls in [
          Repo
      ]}
  setup_argparser(argparser, cmds)

  try:
    import argcomplete
    argcomplete.autocomplete(argparser)
  except ImportError:
    pass

  args = argparser.parse_args()
  argdict = get_argdict(args)

  cmdobj = cmds[args.command](None, **argdict)
  cmdobj(None, **argdict)


if __name__ == "__main__":
  sys.exit(main())
