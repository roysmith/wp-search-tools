#!/usr/bin/env python3

"""A Celery worker process which parses XML dumps and indexes
the comments in elasticsearch.

Start with:

  celery -A tasks worker --loglevel=INFO

If DJANGO_SETTINGS_MODULE is set in the environment, you'll get some
spurious ERR_NOT_INSTALLED warnings.  You can safely ignore these, or
unset DJANGO_SETTINGS_MODULE before starting celery.

"""

from argparse import ArgumentParser
import bz2
from configparser import ConfigParser
import glob
import logging
import os
from pathlib import Path

from celery import Celery
from opensearchpy import OpenSearch

from dump_file import PagesDumpFile


config = ConfigParser()
config.read(Path.home() / '.elasticsearch.ini')
config.read(Path(os.environ['SEARCH_TOOLS']) / 'wp_search_tools/indexer/config.ini')

app = Celery(broker=config.get('celery', 'broker'),
             backend=config.get('celery', 'backend'))


@app.task
def process_path(path):
    user = config.get('elasticsearch', 'user')
    password = config.get('elasticsearch', 'password')
    server = config.get('elasticsearch', 'server')
    index_name = config.get('elasticsearch', 'index')

    es = OpenSearch(server, http_auth=(user, password))
    es.indices.create(index_name, ignore=400)

    count = 0
    logging.info('Processing file "%s"', path)
    df = PagesDumpFile(path)
    for revision in df.process():
        logging.info(revision)
        es.index(index_name, revision)
        count += 1

    return count
