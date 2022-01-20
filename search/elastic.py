#!/usr/bin/env python3

from pprint import pprint
from opensearchpy import OpenSearch


def main():

    es = OpenSearch(['elasticsearch.svc.tools.eqiad1.wikimedia.cloud:80'])
    pprint(es.indices.get('*'))


if __name__ == '__main__':
    main()
