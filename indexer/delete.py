#!/usr/bin/env python3

from configparser import ConfigParser
import os
from pathlib import Path

from opensearchpy import OpenSearch


config = ConfigParser()
config.read(Path.home() / '.elasticsearch.ini')
config.read(Path(os.environ['SEARCH_TOOLS']) / 'wp_search_tools/indexer/config.ini')

user = config.get('elasticsearch', 'user')
password = config.get('elasticsearch', 'password')
server = config.get('elasticsearch', 'server')
index_name = config.get('elasticsearch', 'index')

es = OpenSearch(server, http_auth=(user, password))

# This is dangerous.  Don't do this unless you really are sure you want
# to drop the index, potentially destroying a large amount of work.
#
# If you're sure, un-comment the following line (but don't commit that
# back to version control).
#
# es.indices.delete(index_name)
