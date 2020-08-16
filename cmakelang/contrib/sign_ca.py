"""
Generate the copyright assignment document from the template, and optionally
sign it with gpg.
"""

import argparse
import collections
import io
import json
import os
import subprocess
import sys
import tempfile


def get_signature_packet(infile):
  """
  Return the ascii-armored signature packet between the lines:
  -----BEGIN PGP SIGNATURE-----

  <packet-content>
  -----END PGP SIGNATURE-----
  """

  lineiter = iter(infile)
  for line in lineiter:
    if "BEGIN PGP SIGNATURE" in line:
      break

  packetlines = []
  next(lineiter)
  for line in lineiter:
    if "END PGP SIGNATURE" in line:
      return packetlines
    packetlines.append(line.strip())

  raise ValueError("no PGP BEGIN/END tags in file content!")


def generate_document(args):
  thisdir = os.path.dirname(os.path.realpath(__file__))
  with io.open(os.path.join(thisdir, "individual_ca.txt"),
               encoding="utf-8") as infile:
    output_text = infile.read()
  output_text = output_text.replace(r"{{signer_name}}", args.name)
  output_text = output_text.replace(r"{{signer_email}}", args.email)

  with io.open(args.output_text, "w", encoding="utf-8") as outfile:
    outfile.write(output_text)

  if args.only_template:
    print(
        "The contributor agreement has been written to {}, please sign it with "
        "GPG and include the signature in your first contribution"
        .format(args.output_text))
    return

  argv = ["gpg", "--output", args.output_sig]
  if args.signkey is not None:
    argv.extend(["--default-key", args.signkey])
  argv.extend(["--armor", "--detach-sign", args.output_text])
  subprocess.call(argv)
  print(
      "The contributor agreement has been written to {}, and the signature "
      "has been written to {}"
      .format(args.output_text, args.output_sig))


def setup_parser(parser):
  """
  Configure command line parser
  """
  default_name = None
  try:
    default_name = subprocess.check_output(
        ["git", "config", "user.name"]).decode("utf-8").strip()
  except subprocess.CalledProcessError:
    pass

  default_email = None
  try:
    default_email = subprocess.check_output(
        ["git", "config", "user.email"]).decode("utf-8").strip()
  except subprocess.CalledProcessError:
    pass

  default_signkey = None
  try:
    default_signkey = subprocess.check_output(
        ["git", "config", "user.signingkey"]).decode("utf-8").strip()
  except subprocess.CalledProcessError:
    pass

  parser.add_argument(
      "-n", "--name",
      default=default_name,
      required=(default_name is None),
      help=("Your name (to fill in the agreement template). Default={}"
            .format(default_name)))

  parser.add_argument(
      "-e", "--email",
      default=default_email,
      required=(default_email is None),
      help=("Your name (to fill in the agreement template). Default={}"
            .format(default_email)))

  parser.add_argument(
      "-k", "--signkey",
      default=default_signkey,
      help=("Which signing key to use if you don't want to use your gpg "
            "default. Default={}".format(default_signkey)))

  default_outpath = os.path.join(tempfile.gettempdir(), "cmake-format-ca.txt")
  default_sigout = os.path.join(tempfile.gettempdir(), "cmake-format-ca.sig")
  parser.add_argument(
      "-o", "--output-text", default=default_outpath,
      help=r"Where to write out the agreement text. Default is"
           r"/{tempdir}/cmake-format-ca.txt")
  parser.add_argument(
      "-s", "--output-sig", default=default_sigout,
      help=r"Where to write out the signature. Default is"
           r"/{tempdir}/cmake-format-ca.sig")

  parser.add_argument(
      "-t", "--only-template", action="store_true",
      help="Don't attempt to sign the document with gpg, just fill in the"
           " template and write to a file.")


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  setup_parser(parser)
  args = parser.parse_args()
  generate_document(args)
  if args.only_template:
    return 0

  with io.open(args.output_sig, "r", encoding="utf-8") as infile:
    packetlines = get_signature_packet(infile)

  dataitem = collections.OrderedDict([
      ("template", "individual"),
      ("version", "1.0"),
      ("name", args.name),
      ("email", args.email),
      ("signature", packetlines)
  ])

  thisdir = os.path.dirname(os.path.realpath(__file__))
  database_path = os.path.join(thisdir, "signature_db.json")
  with io.open(database_path, "r", encoding="utf-8") as infile:
    database = json.load(infile, object_pairs_hook=collections.OrderedDict)
  database.append(dataitem)
  with io.open(database_path, "w", encoding="utf-8") as outfile:
    json.dump(database, outfile, indent=2)
  return 0


if __name__ == "__main__":
  sys.exit(main())
