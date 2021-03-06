import bz2
from io import StringIO
from pprint import pprint
from unittest import TestCase
from unittest.mock import Mock, call, patch, mock_open

from wp_search_tools.indexer.dump_file import PagesDumpFile, RevisionData


class PagesDumpFileTest(TestCase):

    def test_construct(self):
        df = PagesDumpFile()


    def test_reports_zero_pages_and_zero_revisions_before_procesing(self):
        df = PagesDumpFile()
        self.assertEqual(df.pages, 0)
        self.assertEqual(df.revisions, 0)


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
            self.assertEqual(docs, [RevisionData(1, 999, 'name', 'text')])


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
            self.assertEqual(docs, [RevisionData(1, 101, 'name 1', 'comment 1'),
                                    RevisionData(1, 102, 'name 2', 'comment 2'),
                                    RevisionData(2, 201, 'name 3', 'comment 3')])


    def test_page_and_revision_counts_are_reported_correctly(self):
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
            list(df.process('xxx'))
            m.assert_called_once_with('xxx')
            self.assertEqual(df.pages, 2)
            self.assertEqual(df.revisions, 3)


    def test_empty_comment_generates_empty_comment_string(self):
        data = '''
        <mediawiki>
          <page>
            <id>1</id>
            <revision>
              <id>999</id>
              <contributor>
                <username>name</username>
              </contributor>
              <comment></comment>
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
            self.assertEqual(docs, [RevisionData(1, 999, 'name', '')])


    def test_missing_comment_generates_empty_comment_string(self):
        data = '''
        <mediawiki>
          <page>
            <id>1</id>
            <revision>
              <id>999</id>
              <contributor>
                <username>name</username>
              </contributor>
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
            self.assertEqual(docs, [RevisionData(1, 999, 'name', '')])


    def test_deleted_comment_generates_none(self):
        data = '''
        <mediawiki>
          <page>
            <id>1</id>
            <revision>
              <id>999</id>
              <contributor>
                <username>name</username>
              </contributor>
              <comment deleted="deleted"/>
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
            self.assertEqual(docs, [RevisionData(1, 999, 'name', None)])
