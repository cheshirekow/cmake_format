
import unittest
import subprocess

from cmake_format import parse_funs

IGNORE_LIST = [
    "endforeach",
    "endfunction",
    "endmacro"
]


class TestCommandDatabase(unittest.TestCase):
  """
  Execute cmake and ensure that all cmake commands are in the database
  """

  def test_all_commands_in_db(self):
    missing_commands = []
    proc = subprocess.Popen(
        ["cmake", "--help-command-list"],
        stdout=subprocess.PIPE)

    parse_db = parse_funs.get_parse_db()

    ignore = IGNORE_LIST
    with proc.stdout as infile:
      for line in infile:
        command = line.strip().decode("utf-8")
        if command not in parse_db and command not in ignore:
          missing_commands.append(command)
    proc.wait()

    message = "Missing commands:\n  " + "\n  ".join(sorted(missing_commands))
    self.assertFalse(bool(missing_commands), msg=message)


if __name__ == "__main__":
  unittest.main()
