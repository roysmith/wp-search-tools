#!/usr/bin/env python3

from argparse import ArgumentParser
from configparser import ConfigParser
import json
import logging
import os
from pathlib import Path
from pprint import pprint
import sys

from opensearchpy import OpenSearch


def main():
    logging.basicConfig(level=logging.WARNING)
    parser = ArgumentParser()
    parser.add_argument('--config', '-c', default='config.ini',
                        help='config file (default %(default)s)')
    parser.add_argument('--file', '-f',
                        help='input file (over-rides config')
    parser.add_argument('--stats', action='store_true',
                        help='print index stats')
    parser.add_argument('--search', nargs='*',
                        help='search term')
    args = parser.parse_args()

    config = ConfigParser()
    config.read(get_configs())
    user = config.get('elasticsearch', 'user')
    password = config.get('elasticsearch', 'password')
    server = config.get('elasticsearch', 'server')
    index_name = config.get('elasticsearch', 'index')

    es = OpenSearch(server, http_auth=(user, password))

    if args.search:
        return search(es, index_name, args.search)
    if args.stats:
        return stats(es, index_name)


def search(es, index_name, words):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"comment": ' '.join(words)}},
                    ]
                }
            }
        }

    pprint(es.search(body=query, index=index_name))


def stats(es, index_name):
    data = es.count(index=index_name)
    print(f'index "{index_name}" has {data.get("count")} items')


def get_configs():
    """Returns a interable over all the config files to read.

    """
    yield Path.home() / '.elasticsearch.ini'
    if 'SEARCH_TOOLS' in os.environ:
        yield Path(os.environ['SEARCH_TOOLS']) / 'src/elasticsearch.ini'
    yield Path('elasticsearch.ini')


if __name__ == '__main__':
    main()
