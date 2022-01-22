#!/usr/bin/env python3

from argparse import ArgumentParser
import bz2
from configparser import ConfigParser
import glob
import logging
import os
from pathlib import Path
from pprint import pprint
from xml.dom import pulldom

from opensearchpy import OpenSearch
from dump_file import PagesDumpFile


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('--config', '-c', default='config.ini',
                        help='config file (default %(default)s)')
    parser.add_argument('--file', '-f',
                        help='input file (over-rides config')

    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.config)
    config.read(Path.home() / '.elasticsearch.ini')
    config.read(Path(os.environ['SEARCH_TOOLS']) / 'src/elasticsearch.ini')

    if args.file:
        logging.info('Processing command-line file "%s"', args.file)
        process_path(args.file, config)
    else:
        pattern = config.get('dumps', 'path_glob')
        logging.info('Processing directory "%s"', pattern)
        for path in glob.iglob(pattern):
            process_path(path, config)


def process_path(path, config):
    logging.info('Processing file "%s"', path)
    df = PagesDumpFile(path)
    for revision in df.process():
        logging.info(revision)

if __name__ == '__main__':
    main()
