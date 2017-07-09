from __future__ import print_function
import argparse
import sys

import cmakelists_parsing.parsing as cmp

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Pretty-print CMakeLists files.')
    parser.add_argument('files', type=str, nargs='*',
                        help='files to pretty print (default is stdin)')
    parser.add_argument('-t', '--tree', action='store_true',
                        help='print out the syntax trees')
    args = parser.parse_args()

    # Gather files
    filenames = args.files
    files = [('<stdin>', sys.stdin)]
    if filenames:
        files = [(name, open(name)) for name in filenames]

    # Process files
    for (name, file) in files:
        with file:
            input = file.read()
            tree = cmp.parse(input, path=name)
            if args.tree:
                # Print out AST
                print(repr(tree))
            else:
                # Pretty print
                print(str(tree), end='')

if __name__ == '__main__':
    main()
