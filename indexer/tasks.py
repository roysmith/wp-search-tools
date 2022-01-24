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
from wp_search_tools.utils.progress import ProgressMonitor

logger = logging.getLogger('wp_search_tools.tasks')
progress_logger = ProgressMonitor(logger, count=10)


config = ConfigParser()
config.read(Path.home() / '.elasticsearch.ini')
config.read(Path(os.environ['SEARCH_TOOLS']) / 'wp_search_tools/indexer/config.ini')

app = Celery(broker=config.get('celery', 'broker'),
             backend=config.get('celery', 'backend'))


@app.task
def process_path(path, expected_pages):
    """Ingest a dump file and index each of the revisions.

    path is an absolute path to the dump file.  If the path ends
    in in .bz2, it is decompressed on the fly.

    expected_pages is the number of pages which are expected to be in
    the dump file.  This is only used to produce useful log messages
    about job progress, so an exact count is not essential.

    Returns a dict with status information.

    """
    user = config.get('elasticsearch', 'user')
    password = config.get('elasticsearch', 'password')
    server = config.get('elasticsearch', 'server')
    index_name = config.get('elasticsearch', 'index')

    es = OpenSearch(server, http_auth=(user, password))
    es.indices.create(index_name, ignore=400)

    page_count = 0
    previous_page_id = None
    revision_count = 0

    logger.info('Processing file "%s"', path)
    df = PagesDumpFile()
    for revision in df.process(path):
        es.index(index_name, revision)
        revision_count += 1
        page_id = revision['page_id']
        if page_id != previous_page_id:
            page_count += 1
            previous_page_id = page_id
        percent = (100.0 * page_count) / expected_pages
        progress_logger.info('Done with %d of %d (%.0f%%) pages', page_count, expected_pages, percent)

    return {'pages': page_count,
            'revisions': revision_count,
            }
