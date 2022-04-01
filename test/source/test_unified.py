import unittest
from data.source.pipeline import unified_string_source_pipe


class TestUnifiedSource(unittest.TestCase):

    def test_without_unification(self):
        content = 'This is my source string'
        unified_source = unified_string_source_pipe(content)
        for char in content:
            self.assertEqual(unified_source.next_char(), char, 'Characters should match')
        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')

    def test_windows_unification(self):
        unified_source = unified_string_source_pipe('\r\n')
        self.assertEqual(unified_source.next_char(), '\n', 'Expected new line character')
        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')

    def test_risc_newline(self):
        unified_source = unified_string_source_pipe('\n\r')
        self.assertEqual(unified_source.next_char(), '\n', 'Expected new line character')
        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')

    def test_linux_newline(self):
        unified_source = unified_string_source_pipe('\n')
        self.assertEqual(unified_source.next_char(), '\n', 'Expected new line character')
        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')

    def test_ibm_newline(self):
        unified_source = unified_string_source_pipe('\025')
        self.assertEqual(unified_source.next_char(), '\n', 'Expected new line character')
        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')

    def test_with_unification(self):
        content = 'This \n is \025 new \n\r sequence \r\n for \r test \r\r \n\n\025'
        expected = 'This \n is \n new \n sequence \n for \r test \r\r \n\n\n'
        unified_source = unified_string_source_pipe(content)

        for char in expected:
            self.assertEqual(unified_source.next_char(), char, 'Characters should match')

        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')

    def test_all_new_lines(self):
        content = '\n\n\r\r\n\025'
        expected = '\n\n\n\n'
        unified_source = unified_string_source_pipe(content)

        for char in expected:
            self.assertEqual(unified_source.next_char(), char, 'Characters should match')

        self.assertEqual(unified_source.next_char(), '', 'Expected empty char (EOF)')


if __name__ == '__main__':
    unittest.main()
