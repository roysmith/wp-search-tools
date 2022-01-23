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


class PagesDumpFile:

    def __init__(self, path):
        """Path is the file to be parsed.  If it ends in '.bz2', it is
        decompressed on the fly.

        """
        self.path = path


    def process(self):
        opener = bz2.open if self.path.endswith('.bz2') else open
        stream = opener(self.path)
        return self.process_stream(stream)


    def process_stream(self, stream):
        logging.debug('process_stream(%s)', stream)
        doc = pulldom.parse(stream)
        for event, node in doc:
            if event == pulldom.START_ELEMENT and node.tagName == 'page':
                doc.expandNode(node)
                page_node = node
                page_id = page_node.getElementsByTagName('id')[0].childNodes[0].nodeValue

                for revision in page_node.getElementsByTagName('revision'):
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

                    output_doc = {'page_id': int(page_id),
                                  'rev_id': int(rev_id),
                                  'user': user,
                                  'comment': comment
                                  }
                    yield output_doc
