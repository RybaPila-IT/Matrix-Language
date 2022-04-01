import unittest
from data.source.pipeline import positional_string_source_pipe


class TestPositionalSource(unittest.TestCase):
    def test_positioning(self):
        content = '1234\n\n\r\r\n\0251234'
        expected = '1234\n\n\n\n1234'
        positions = [
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
            (5, 4),
        ]
        pos_source = positional_string_source_pipe(content)
        for pos, char in zip(positions, expected):
            self.assertEqual(pos[0], pos_source.position()[0])
            self.assertEqual(pos[1], pos_source.position()[1])
            self.assertEqual(char, pos_source.next_char())
        self.assertEqual('', pos_source.next_char())
        self.assertEqual(positions[len(positions) - 1][0], pos_source.position()[0])
        self.assertEqual(positions[len(positions) - 1][1] + 1, pos_source.position()[1])


if __name__ == '__main__':
    unittest.main()
