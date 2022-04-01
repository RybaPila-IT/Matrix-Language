import unittest
from data.source.raw import RawStringSource


class TestRawStringSource(unittest.TestCase):
    def test_source_next_char(self):
        content = 'This is sample content \r\n \n'
        source = RawStringSource(content)
        for char in content:
            self.assertEqual(source.next_char(), char, 'Characters should match')
        self.assertEqual(source.next_char(), '', 'Expected empty char (EOF')


if __name__ == '__main__':
    unittest.main()
