#!/usr/bin/env python3

from argparse import ArgumentParser
from pprint import pprint
import re
from tasks import process_path


def main():
    parser = ArgumentParser()
    parser.add_argument('path',
                        help='dump file to index')
    parser.add_argument('--dry-run', action='store_true',
                        help="don't insert revisions into elasticsearch")
    args = parser.parse_args()

    m = re.search(r'-p(\d*)p(\d*)', args.path)
    if not m:
        print(f"Can't find page numbers in {args.path}")
        return -1
    p1 = int(m[1])
    p2 = int(m[2])
    count = p2 - p1 + 1

    pprint(f'Processing {args.path} with {count} expected pages')
    result = process_path.delay(args.path, count, args.dry_run)
    print(result.get())

if __name__ == '__main__':
    main()
