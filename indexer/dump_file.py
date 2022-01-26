"""Wrapper around a Wikipedia 'pages' XML dump file.

This should be able to process any of:

  <wikiname>-YYYYMMDD-pages-articles*.xm-l*.bz2
  <wikiname>-YYYYMMDD-pages-meta-current*.xml-*.bz2
  <wikiname>-YYYYMMDD-pages-meta-history*.xml-*.bz2

although it has only been tested with enwiki.  See
meta.wikimedia.org/wiki/Data_dumps/Dump_format for details.

"""

import bz2
from dataclasses import dataclass
import logging
from xml.dom import pulldom

logger = logging.getLogger('wp_search_tools.tasks')

@dataclass(frozen=True)
class RevisionData:
    """A deleted comment is represented as None.  A revision which simply
    has no comment will have comment set to the empty string.

    """
    page_id: int
    rev_id: int
    user: str
    comment: str


class PagesDumpFile:

    def __init__(self):
        self.pages = 0
        self.revisions = 0


    def process(self, path):
        """Path is the file to be parsed.  If it ends in '.bz2', it is
        decompressed on the fly.

        Returns an iterator over RevisionData objects.

        """
        logger.debug('process(%s)', path)
        opener = bz2.open if path.endswith('.bz2') else open
        with opener(path) as stream:
            doc = pulldom.parse(stream)
            state = ''
            for event, node in doc:
                if event == pulldom.START_ELEMENT:
                    if node.tagName == 'page':
                        state = 'page'
                        self.pages += 1
                        page_id = None
                        continue
                    elif state == 'page' and node.tagName == 'id':
                        doc.expandNode(node)
                        page_id = int(node.childNodes[0].nodeValue)
                        continue
                    elif state == 'page' and node.tagName == 'revision':
                        state = 'revision'
                        self.revisions += 1
                        doc.expandNode(node)
                        rev_id = int(node.getElementsByTagName('id')[0].childNodes[0].nodeValue)

                        contributor = node.getElementsByTagName('contributor')[0]
                        usernames = contributor.getElementsByTagName('username')
                        if usernames:
                            user_node = usernames[0]
                        else:
                            user_node = contributor.getElementsByTagName('ip')[0]
                        user = user_node.childNodes[0].nodeValue

                        comment_nodes = node.getElementsByTagName('comment')
                        if comment_nodes:
                            comment_node = comment_nodes[0]
                            if comment_node.hasAttribute('deleted'):
                                comment = None
                            else:
                                child = comment_node.firstChild
                                comment = (child and child.nodeValue) or ''
                        else:
                            comment = ''

                        state = 'page'
                        yield RevisionData(page_id, rev_id, user, comment)
                        continue
