import unittest

# pylint: disable=unused-import
from cmake_format.command_tests import (
    TestAddCustomCommand,
    TestConditional,
    TestCustomCommand,
    TestExport,
    TestExternalProject,
    TestFile,
    TestForeach,
    TestInstall,
    TestSetTargetProperties,
    TestSet,)

from cmake_format.command_tests.add_executable_tests \
    import TestAddExecutableCommand
from cmake_format.command_tests.add_library_tests \
    import TestAddLibraryCommand
from cmake_format.command_tests.misc_tests \
    import TestMiscFormatting


def main():
  unittest.main()


if __name__ == "__main__":
  main()
