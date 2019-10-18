import unittest

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=unused-import

from cmake_format.invocation_tests import *
from cmake_format.layout_tests import *
from cmake_format.lexer_tests import *
from cmake_format.markup_tests import *
from cmake_format.parser_tests import *

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
from cmake_format.contrib.validate_database \
    import TestContributorAgreements
from cmake_format.contrib.validate_pullrequest \
    import TestContribution
from cmake_format.doc.docsources_test \
    import TestDocSources
from cmake_format.test.version_number_test \
    import TestVersionNumber

if __name__ == '__main__':
  unittest.main()
