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
from celery.signals import after_setup_logger
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

@after_setup_logger.connect
def setup_loggers(logger, format, **kwargs):
    logdir = Path(os.environ['SEARCH_TOOLS']) / 'logs'
    logfile = logdir / 'celery.log'
    logdir.mkdir(exist_ok=True)
    formatter = logging.Formatter(format)
    handler = logging.handlers.TimedRotatingFileHandler(logfile,
                                                        when='midnight',
                                                        utc=True,
                                                        backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@app.task
def process_path(path, expected_pages, dry_run=False):
    """Ingest a dump file and (optionally) index each of the revisions.

    path is an absolute path to the dump file.  If the path ends
    in in .bz2, it is decompressed on the fly.

    expected_pages is a rough estimate of the number of pages which
    are expected to be in the dump file.  This is only used to produce
    log messages about job progress, so an exact count is not immportant.

    If dry_run is true, the dump file is parsed as normal, but
    revisions are not uploaded to elasticsearch,

    Returns a dict with status information.

    """
    user = config.get('elasticsearch', 'user')
    password = config.get('elasticsearch', 'password')
    server = config.get('elasticsearch', 'server')
    index_name = config.get('elasticsearch', 'index')

    es = OpenSearch(server, http_auth=(user, password))
    es.indices.create(index_name, ignore=400)

    logger.info('Processing file "%s"', path)
    df = PagesDumpFile()
    for revision in df.process(path):
        if not dry_run:
            es.index(index_name, revision)
        percent = (100.0 * df.pages) / expected_pages
        progress_logger.info('Done with %d of %d (%.0f%%) pages', df.pages, expected_pages, percent)

    return {'pages': df.pages,
            'revisions': df.revisions,
            }
