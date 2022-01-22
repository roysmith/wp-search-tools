import bz2
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, call, patch, mock_open

from dump_file import PagesDumpFile


class ProgressTest(TestCase):

    def test_construct(self):
        df = PagesDumpFile('foo')
        self.assertEqual(df.path, 'foo')


    def test_builtin_open_is_called_with_normal_path(self):
        m = mock_open()
        with patch('dump_file.open', new=m):
            df = PagesDumpFile('foo')
            df.process()
            m.assert_called_once_with('foo')


    def test_bz2_open_is_called_with_bz2_path(self):
        with patch('dump_file.bz2.open', autospec=True) as m:
            m.return_value = StringIO()
            df = PagesDumpFile('foo.bz2')
            df.process()
            m.assert_called_once_with('foo.bz2')


    def test_empty_input_generates_no_items(self):
        stream = StringIO('')
        df = PagesDumpFile('')
        docs = list(df.process_stream(stream))
        self.assertEqual(docs, [])


    def test_xml_with_one_revision_generates_one_item(self):
        data = '''
        <mediawiki>
          <page>
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
        stream = StringIO(data)
        df = PagesDumpFile('')
        docs = list(df.process_stream(stream))
        self.assertEqual(docs, [{'rev_id': 999, 'user': 'name', 'comment': 'text'}])


    def test_xml_with_multiple_revision_generates_one_item_per_revision(self):
        data = '''
        <mediawiki>
          <page>
            <revision>
              <id>1</id>
              <contributor>
                <username>name 1</username>
              </contributor>
              <comment>comment 1</comment>
            </revision>
            <revision>
              <id>2</id>
              <contributor>
                <username>name 2</username>
              </contributor>
              <comment>comment 2</comment>
            </revision>
          </page>
          <page>
            <revision>
              <id>3</id>
              <contributor>
                <username>name 3</username>
              </contributor>
              <comment>comment 3</comment>
            </revision>
          </page>
        </mediawiki>
        '''
        stream = StringIO(data)
        df = PagesDumpFile('')
        docs = list(df.process_stream(stream))
        self.assertEqual(docs, [{'rev_id': 1, 'user': 'name 1', 'comment': 'comment 1'},
                                {'rev_id': 2, 'user': 'name 2', 'comment': 'comment 2'},
                                {'rev_id': 3, 'user': 'name 3', 'comment': 'comment 3'},
                                ])
