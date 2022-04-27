import unittest

# noinspection PyProtectedMember
from execution.interpreter import Interpreter, _Variable, _VariableType
from syntax_tree.constructions import *


class TestInterpreter(unittest.TestCase):
    def test_number_literal_evaluation(self):
        """
        Test number literal evaluation by parser.
        """
        interpreter = Interpreter(None)
        number_literal = NumberLiteral(42)
        expected_result = _Variable(_VariableType.NUMBER, 42)
        interpreter.evaluate_number_literal(number_literal)
        self.assertEqual(expected_result, interpreter.result)

    def test_string_literal_evaluation(self):
        """
        Test string literal evaluation by parser.
        """
        interpreter = Interpreter(None)
        string_literal = StringLiteral('Lorem ipsum')
        expected_result = _Variable(_VariableType.STRING, 'Lorem ipsum')
        interpreter.evaluate_string_literal(string_literal)
        self.assertEqual(expected_result, interpreter.result)


if __name__ == '__main__':
    unittest.main()