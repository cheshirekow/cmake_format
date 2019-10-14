import unittest

# pylint: disable=unused-import
from cmake_format.command_tests.add_custom_command_tests \
  import TestAddCustomCommand
from cmake_format.command_tests.add_executable_tests \
    import TestAddExecutableCommand
from cmake_format.command_tests.add_library_tests \
    import TestAddLibraryCommand
from cmake_format.command_tests.conditional_tests \
    import TestConditionalCommands
from cmake_format.command_tests.export_tests \
    import TestExportCommand
from cmake_format.command_tests.file_tests \
    import TestFileCommands
from cmake_format.command_tests.install_tests \
    import TestInstallCommands
from cmake_format.command_tests.misc_tests \
    import TestMiscFormatting
from cmake_format.command_tests.set_tests \
    import TestSetCommand


def main():
  unittest.main()


if __name__ == "__main__":
  main()
