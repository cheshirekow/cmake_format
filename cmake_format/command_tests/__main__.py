import unittest

# pylint: disable=unused-import
from cmake_format.command_tests import (
    TestAddCustomCommand,
    TestConditional,
    TestExport,
    TestExternalProject,
    TestForeach,
    TestFile,
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
