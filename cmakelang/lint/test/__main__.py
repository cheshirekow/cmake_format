from __future__ import print_function, unicode_literals

import sys
import unittest

# pylint: disable=W0401,W0611,W0614
from cmakelang.lint.test import genfiles
from cmakelang.lint.test.expect_tests import gen_test_classes, ConfigTestCase
from cmakelang.lint.test.execution_tests import TestFormatFiles

if __name__ == "__main__":
  classnames = [
      "ConfigTestCase",
      "TestFormatFiles",
  ]

  classobj = None
  for classobj in gen_test_classes():
    globals()[classobj.__name__] = classobj
    classnames.append(classobj.__name__)
  del classobj

  if len(sys.argv) > 1 and sys.argv[1] == "print-names":
    print("\n".join(sorted(classnames)))
    sys.exit(0)

  unittest.main()
