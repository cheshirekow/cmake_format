import glob
import os
import unittest

import cmakelists_parsing.parsing as cmp

def yield_examples():
    paths = glob.glob(os.path.join(os.path.dirname(__file__),
                                   '..', 'example_inputs', '*'))
    for path in paths:
        with open(path) as file:
            contents = file.read()
            yield path, contents

class ExamplesTestCase(unittest.TestCase):
    def test_idempotency_of_parse_unparse(self):
        round_trip = lambda s, path='<string>': str(cmp.parse(s, path))
        for path, contents in yield_examples():
            self.assertEqual(round_trip(contents, path),
                             round_trip(round_trip(contents, path)),
                             'Failed on %s' % path)

    def test_tree_is_unchanged(self):
        for path, contents in yield_examples():
            expected = cmp.parse(contents, path)
            actual = cmp.parse(str(cmp.parse(contents, path)))
            msg = 'Failed on %s.\nExpected\n%s\n\nGot\n%s' % (path, expected, actual)
            self.assertEqual(expected, actual, msg)
