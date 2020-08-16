import unittest

# pylint: disable=unused-import
from cmakelang.command_tests import (
    TestAddCustomCommand,
    TestConditional,
    TestComment,
    TestCustomCommand,
    TestExport,
    TestExternalProject,
    TestFile,
    TestForeach,
    TestInstall,
    TestSetTargetProperties,
    TestSet)

from cmakelang.command_tests.add_executable_tests \
    import TestAddExecutableCommand
from cmakelang.command_tests.add_library_tests \
    import TestAddLibraryCommand
from cmakelang.command_tests.misc_tests \
    import TestMiscFormatting


def main():
  unittest.main()


if __name__ == "__main__":
  main()
