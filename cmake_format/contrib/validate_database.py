# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import unittest
import shutil
import subprocess
import sys
import tempfile
import warnings


def get_repo_dir():
  """
  Return the path to the repository root
  """
  thisdir = os.path.dirname(os.path.realpath(__file__))
  parent, _ = os.path.split(thisdir)
  parent, _ = os.path.split(parent)
  return parent


def format_signature(armored_packet):
  """
  Append the common that were stripped out of the signature when stored in the
  database.
  """
  return "\n".join(
      ["-----BEGIN PGP SIGNATURE-----", ""]
      + armored_packet
      + ["-----END PGP SIGNATURE-----"]) + "\n"


def construct_agreement_text(template, dataitem):
  """
  Re-construct the agreement text.
  """
  template = template.replace("{{signer_name}}", dataitem["name"])
  template = template.replace("{{signer_email}}", dataitem["email"])
  return template


class TestContributorAgreements(unittest.TestCase):
  """
  Validate the signature in the contributor database.
  """

  def __init__(self, *args, **kwargs):
    super(TestContributorAgreements, self).__init__(*args, **kwargs)
    self.homedir = None

  def setUp(self):
    self.homedir = tempfile.mkdtemp(prefix="gpgtmp")

  def tearDown(self):
    shutil.rmtree(self.homedir)

  def test_signatures(self):
    """
    Iterate over signatures and verify them.
    """
    gpg_argv = ["gpg", "--homedir", self.homedir]

    if sys.version_info < (3, 0, 0):
      self.skipTest("no pgpy on this python version")

    # TODO(josh): For some reason importing pgpy seems to cause the
    # stderr filedescriptor to leak when we subprocess below. pgpy must be
    # doing some ugly subprocess thing on it's own
    warnings.simplefilter("ignore", ResourceWarning)

    # TODO(josh): pgpy seems to import distutils and the version distributed
    # with virtualenv on this system has an outdated import of `imp` instead
    # of `importlib`.
    with warnings.catch_warnings():
      warnings.simplefilter("ignore", DeprecationWarning)
      import pgpy  # pylint: disable=import-error

    repodir = get_repo_dir()
    with open(os.path.join(
        repodir, "cmake_format/contrib/signature_db.json")) as infile:
      sigdb = json.load(infile)

    # First, get a list of keys already in the local keyring
    known_fingerprints = set()
    proc = subprocess.Popen(
        gpg_argv + ["--fingerprint", "--with-colons"],
        stdout=subprocess.PIPE)
    for line in proc.stdout:
      parts = line.decode("utf-8").split(":")
      if parts[0] == "fpr":
        fingerprint = parts[-2]
        known_fingerprints.add(fingerprint[-16:])
    proc.wait()

    # Now do a scan through the database and get a list of any keys we are
    # missing
    needkeys = []
    for sigentry in sigdb:
      clearsign = format_signature(sigentry["signature"])
      sig = pgpy.PGPSignature()
      sig.parse(clearsign)
      if sig.signer not in known_fingerprints:
        needkeys.append(sig.signer)

    if needkeys:
      # TODO(josh): use SKS pool instead of specific server
      result = subprocess.check_call(
          gpg_argv + ["--keyserver", "keyserver.ubuntu.com", "--recv-keys"]
          + needkeys)
      self.assertEqual(
          result, 0, msg="Failed to fetch all keys from keyserver")

    with open(os.path.join(
        repodir, "cmake_format/contrib/individual_ca.txt")) as infile:
      template = infile.read()

    # Then verify all the signatures
    for sigentry in sigdb:
      clearsign = format_signature(sigentry["signature"])
      document = construct_agreement_text(template, sigentry)
      with tempfile.NamedTemporaryFile(delete=False) as outfile:
        outfile.write(clearsign.encode("utf-8"))
        detached_sig = outfile.name
      with tempfile.NamedTemporaryFile(delete=False) as outfile:
        outfile.write(document.encode("utf-8"))
        document_msg = outfile.name

      with open(os.devnull, "w") as devnull:
        proc = subprocess.Popen(
            gpg_argv + ["--verify", detached_sig, document_msg],
            stderr=devnull)
        result = proc.wait()
      self.assertEqual(
          0, result,
          msg="Failed to verify signature for {}\n\n"
              "See {} and {}".format(
                  sigentry["name"], detached_sig, document_msg))
      os.unlink(detached_sig)
      os.unlink(document_msg)


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()
