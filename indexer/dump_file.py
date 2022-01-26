"""Wrapper around a Wikipedia 'pages' XML dump file.

This should be able to process any of:

  <wikiname>-YYYYMMDD-pages-articles*.xm-l*.bz2
  <wikiname>-YYYYMMDD-pages-meta-current*.xml-*.bz2
  <wikiname>-YYYYMMDD-pages-meta-history*.xml-*.bz2

although it has only been tested with enwiki.  See
meta.wikimedia.org/wiki/Data_dumps/Dump_format for details.

"""

import bz2
import logging
from xml.dom import pulldom

logger = logging.getLogger('wp_search_tools.tasks')

class PagesDumpFile:

    def __init__(self):
        self.pages = 0
        self.revisions = 0


    def process(self, path):
        """Path is the file to be parsed.  If it ends in '.bz2', it is
        decompressed on the fly.

        """
        logger.debug('process(%s)', path)
        opener = bz2.open if path.endswith('.bz2') else open
        with opener(path) as stream:
            doc = pulldom.parse(stream)
            for event, node in doc:
                if event == pulldom.START_ELEMENT and node.tagName == 'page':
                    doc.expandNode(node)
                    page_node = node
                    self.pages += 1
                    try:
                        page_id = page_node.getElementsByTagName('id')[0].childNodes[0].nodeValue
                    except IndexError as ex:
                        logger.exception('Could not find page id (page count = %d): %s', self.pages, ex)
                        continue

                    for revision in page_node.getElementsByTagName('revision'):
                        try:
                            self.revisions += 1
                            rev_id = None
                            rev_id = revision.getElementsByTagName('id')[0].childNodes[0].nodeValue

                            contributor = revision.getElementsByTagName('contributor')[0]
                            usernames = contributor.getElementsByTagName('username')
                            if usernames:
                                user_node = usernames[0]
                            else:
                                user_node = contributor.getElementsByTagName('ip')[0]
                            user = user_node.childNodes[0].nodeValue

                            comment_nodes = revision.getElementsByTagName('comment')
                            if comment_nodes:
                                comment = comment_nodes[0].childNodes[0].nodeValue
                            else:
                                comment = ''

                            yield {'page_id': int(page_id),
                                   'rev_id': int(rev_id),
                                   'user': user,
                                   'comment': comment
                            }
                        except IndexError as ex:
                            logger.exception('Could not parse revision in page %s (rev_id %s): %s', page_id, rev_id, ex)
