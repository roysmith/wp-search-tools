import bz2
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, call, patch, mock_open

from wp_search_tools.indexer.dump_file import PagesDumpFile


class PagesDumpFileTest(TestCase):

    def test_construct(self):
        df = PagesDumpFile()


    def test_builtin_open_is_called_with_normal_path(self):
        m = mock_open()
        with patch('wp_search_tools.indexer.dump_file.open', new=m):
            df = PagesDumpFile()
            list(df.process('foo'))
            m.assert_called_once_with('foo')


    def test_bz2_open_is_called_with_bz2_path(self):
        with patch('wp_search_tools.indexer.dump_file.bz2.open', autospec=True) as m:
            m.return_value = StringIO()
            df = PagesDumpFile()
            list(df.process('foo.bz2'))
            m.assert_called_once_with('foo.bz2')


    def test_empty_input_generates_no_items(self):
        stream = StringIO('')
        df = PagesDumpFile()
        docs = list(df.process('/dev/null'))
        self.assertEqual(docs, [])


    def test_xml_with_one_revision_generates_one_item(self):
        data = '''
        <mediawiki>
          <page>
            <id>1</id>
            <revision>
              <id>999</id>
              <contributor>
                <username>name</username>
              </contributor>
              <comment>text</comment>
            </revision>
          </page>
        </mediawiki>
        '''
        m = mock_open()
        with patch('wp_search_tools.indexer.dump_file.open', new=m):
            m.return_value = StringIO(data)
            df = PagesDumpFile()
            docs = list(df.process('xxx'))
            m.assert_called_once_with('xxx')
            self.assertEqual(docs, [{'page_id': 1,
                                     'rev_id': 999,
                                     'user': 'name',
                                     'comment': 'text'}])


    def test_xml_with_multiple_revision_generates_one_item_per_revision(self):
        data = '''
        <mediawiki>
          <page>
            <id>1</id>
            <revision>
              <id>101</id>
              <contributor>
                <username>name 1</username>
              </contributor>
              <comment>comment 1</comment>
            </revision>
            <revision>
              <id>102</id>
              <contributor>
                <username>name 2</username>
              </contributor>
              <comment>comment 2</comment>
            </revision>
          </page>
          <page>
            <id>2</id>
            <revision>
              <id>201</id>
              <contributor>
                <username>name 3</username>
              </contributor>
              <comment>comment 3</comment>
            </revision>
          </page>
        </mediawiki>
        '''
        m = mock_open()
        with patch('wp_search_tools.indexer.dump_file.open', new=m):
            m.return_value = StringIO(data)
            df = PagesDumpFile()
            docs = list(df.process('xxx'))
            m.assert_called_once_with('xxx')
            self.assertEqual(docs, [{'page_id': 1,
                                     'rev_id': 101,
                                     'user': 'name 1',
                                     'comment': 'comment 1'},
                                    {'page_id': 1,
                                     'rev_id': 102,
                                     'user': 'name 2',
                                     'comment': 'comment 2'},
                                    {'page_id': 2,
                                     'rev_id': 201,
                                     'user': 'name 3',
                                     'comment': 'comment 3'}])
