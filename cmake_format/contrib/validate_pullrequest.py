# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import unittest
import subprocess
import sys
import tempfile


def get_repo_dir():
  """
  Return the path to the repository root
  """
  thisdir = os.path.dirname(os.path.realpath(__file__))
  parent, _ = os.path.split(thisdir)
  parent, _ = os.path.split(parent)
  return parent


class TestContribution(unittest.TestCase):
  """
  Verify that contributed code meets requirements
  """

  def __init__(self, *args, **kwargs):
    super(TestContribution, self).__init__(*args, **kwargs)
    self.merge_target = None
    self.merge_feature = None
    self.repodir = None

  def setUp(self):
    if os.environ.get("TRAVIS_PULL_REQUEST", "false") == "false":
      self.skipTest("Not a pull request")
      return

    self.repodir = get_repo_dir()

  def test_single_commit(self):
    """
    Ensure that the pull request is a single commit off of the target
    branch. If it is, then the merge base will be the parent of the feature
    commit.
    """
    repodir = get_repo_dir()
    feature_sha1 = os.environ.get("TRAVIS_PULL_REQUEST_SHA")
    feature_parent = subprocess.check_output(
        ["git", "show", "-s", "--pretty=%P", feature_sha1], cwd=repodir
    ).decode("utf-8").strip()
    self.assertEqual(1, len(feature_parent.split()))

    target_branch = os.environ.get("TRAVIS_BRANCH")
    subprocess.check_call(
        ["git", "fetch", "origin", target_branch],
        cwd=self.repodir)
    merge_base = subprocess.check_output(
        ["git", "merge-base", "FETCH_HEAD", feature_sha1],
        cwd=self.repodir).decode("utf-8").strip()
    self.assertEqual(feature_parent, merge_base)

  def test_merge_base_is_not_too_old(self):
    """
    When we merge a pull request we'll get something like this::

           x -----------
          /             \
   ... - A - o - o - o - B

    where x is the signed commit of the change to pull in. If the commit was
    created "a long time ago" (in a git-sense) then this makes the graph
    difficult to read as there will be lots of very long merge-lines. Therefore
    we require that pull requests be "close-enough" to the current HEAD.
    """
    repodir = get_repo_dir()
    feature_sha1 = os.environ.get("TRAVIS_PULL_REQUEST_SHA")
    target_branch = os.environ.get("TRAVIS_BRANCH")
    subprocess.check_call(
        ["git", "fetch", "origin", target_branch],
        cwd=self.repodir)
    merge_base = subprocess.check_output(
        ["git", "merge-base", "FETCH_HEAD", feature_sha1],
        cwd=self.repodir).decode("utf-8").strip()
    distance_str = subprocess.check_output(
        ["git", "rev-list", "--count", "--first-parent",
         "{}..{}".format(merge_base, "FETCH_HEAD")], cwd=repodir
    ).decode("utf-8")
    distance = int(distance_str)
    self.assertLess(distance, 10)

  def test_commit_is_signed(self):
    """
    Ensure that the feature commit is signed
    """
    repodir = get_repo_dir()
    feature_sha1 = os.environ.get("TRAVIS_PULL_REQUEST_SHA")
    signer_encoded = subprocess.check_output(
        ["git", "show", "-s", r'--pretty="%GK"', feature_sha1],
        cwd=repodir).decode("utf-8").strip().strip('"')

    # TODO(josh): deduplicate with validate_database
    # First, get a list of keys already in the local keyring
    known_fingerprints = set()
    proc = subprocess.Popen(
        ["gpg", "--fingerprint", "--with-colons"],
        stdout=subprocess.PIPE)
    for line in proc.stdout:
      parts = line.decode("utf-8").split(":")
      if parts[0] == "fpr":
        fingerprint = parts[-2]
        known_fingerprints.add(fingerprint[-16:])
    proc.wait()

    if signer_encoded not in known_fingerprints:
      # TODO(josh): use SKS pool instead of specific server
      result = subprocess.check_call(
          ["gpg", "--keyserver", "keyserver.ubuntu.com", "--recv-keys",
           signer_encoded])
      self.assertEqual(
          result, 0, msg="Failed to fetch signer key from keyserver")

    with tempfile.NamedTemporaryFile(delete=False) as stderr:
      result = subprocess.call(
          ["git", "verify-commit", feature_sha1],
          cwd=repodir, stderr=stderr)
      stderrpath = stderr.name
    with open(stderrpath, "r") as infile:
      stderrtext = infile.read()
    os.unlink(stderrpath)
    self.assertEqual(
        0, result,
        "git was unable to verify commit {}\n{}"
        .format(feature_sha1, stderrtext))

  def test_commit_signer_has_signed_ca(self):
    """
    Verify that whoever signed the commit has also signed the contributor
    agreement / copyright assignment.
    """
    if sys.version_info < (3, 0, 0):
      self.skipTest("no pgpy on this python version")
    import pgpy  # pylint: disable=import-error

    repodir = get_repo_dir()
    feature_sha1 = os.environ.get("TRAVIS_PULL_REQUEST_SHA")
    signer_encoded = subprocess.check_output(
        ["git", "show", "-s", r'--pretty="%GK"', feature_sha1],
        cwd=repodir).decode("utf-8").strip().strip('"')

    with open(os.path.join(
        repodir, "cmake_format/contrib/signature_db.json")) as infile:
      sigdb = json.load(infile)

    for sigentry in sigdb:
      clearsign = format_signature(sigentry["signature"])
      sig = pgpy.PGPSignature()
      sig.parse(clearsign)
      if sig.signer == signer_encoded:
        return

    self.fail("Could not find signer {} in signature database"
              .format(signer_encoded))


def format_signature(armored_packet):
  """
  Append the common that were stripped out of the signature when stored in the
  database.
  """
  return "\n".join(
      ["-----BEGIN PGP SIGNATURE-----", ""]
      + armored_packet
      + ["-----END PGP SIGNATURE-----"])


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()
