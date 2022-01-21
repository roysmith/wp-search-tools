#!/usr/bin/env python3

from configparser import ConfigParser
import json
import os
from pathlib import Path
from pprint import pprint
import sys

from opensearchpy import OpenSearch



def main():
    config = ConfigParser()
    config.read(get_configs())
    user = config.get('elasticsearch', 'user')
    password = config.get('elasticsearch', 'password')
    server = config.get('elasticsearch', 'server')
    index_name = config.get('elasticsearch', 'index')

    es = OpenSearch(server, http_auth=(user, password))

    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"user": "AusTerrapin"}},
                    ]
                }
            }
        }

    pprint(es.search(body=query, index=index_name))


def get_configs():
    """Returns a interable over all the config files to read.

    """
    yield Path.home() / '.elasticsearch.ini'
    if 'SEARCH_TOOLS' in os.environ:
        yield Path(os.environ['SEARCH_TOOLS']) / 'src/elasticsearch.ini'
    yield Path('elasticsearch.ini')


if __name__ == '__main__':
    main()
