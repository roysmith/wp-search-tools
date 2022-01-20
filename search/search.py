#!/usr/bin/env python3

from configparser import ConfigParser
import json
from pathlib import Path
from pprint import pprint
import sys

from opensearchpy import OpenSearch


CONFIGS = (Path.home() / '.elasticsearch.ini',
           Path('elasticsearch.ini'))


def main():
    config = ConfigParser()
    config.read(CONFIGS)
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

if __name__ == '__main__':
    main()
