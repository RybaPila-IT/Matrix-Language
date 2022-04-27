import unittest
import numpy as np

# noinspection PyProtectedMember
from execution.interpreter import Interpreter, _Variable, _VariableType
from execution.exception import *
from syntax_tree.constructions import *


class _ErrorExpression:
    def accept(self, visitor):
        raise WithStackTraceException()


class TestInterpreter(unittest.TestCase):
    def test_number_literal_evaluation(self):
        """
        Tests number literal evaluation by parser.
        """
        interpreter = Interpreter(None)
        number_literal = NumberLiteral(42)
        expected_result = _Variable(_VariableType.NUMBER, 42)
        interpreter.evaluate_number_literal(number_literal)
        self.assertEqual(expected_result, interpreter.result)

    def test_string_literal_evaluation(self):
        """
        Tests string literal evaluation by parser.
        """
        interpreter = Interpreter(None)
        string_literal = StringLiteral('Lorem ipsum')
        expected_result = _Variable(_VariableType.STRING, 'Lorem ipsum')
        interpreter.evaluate_string_literal(string_literal)
        self.assertEqual(expected_result, interpreter.result)

    def test_valid_matrix_literal_evaluation(self):
        """
        Tests matrix literal evaluation.

        Test cases are:
            - Single element matrix
            - Single row matrix
            - Multiple rows matrix
        """
        matrix_literals = [
            MatrixLiteral([NumberLiteral(42)], []),
            MatrixLiteral([NumberLiteral(1), NumberLiteral(2), NumberLiteral(3)], [',', ',']),
            MatrixLiteral([
                NumberLiteral(1), NumberLiteral(2), NumberLiteral(3),
                NumberLiteral(4), NumberLiteral(5), NumberLiteral(6),
                NumberLiteral(7), NumberLiteral(8), NumberLiteral(9)
            ], [',', ',', ';', ',', ',', ';', ',', ','])
        ]
        expected_results = [
            _Variable(_VariableType.MATRIX, np.array([[42]])),
            _Variable(_VariableType.MATRIX, np.array([[1, 2, 3]])),
            _Variable(_VariableType.MATRIX, np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
        ]
        for matrix_literal, expected in zip(matrix_literals, expected_results):
            interpreter = Interpreter(None)
            interpreter.evaluate_matrix_literal(matrix_literal)
            self.assertEqual(expected, interpreter.result)

    def test_invalid_matrix_literal_evaluation(self):
        """
        Tests invalid matrix literal evaluation.

        Test cases are:
            - Invalid type in matrix
            - Rows length mismatch
            - Expression evaluation error
        """
        matrix_literals = [
            MatrixLiteral([StringLiteral('Lorem ipsum')], []),
            MatrixLiteral([NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ',', ';']),
            MatrixLiteral([_ErrorExpression()], [])
        ]
        expected_exceptions = [
            InvalidTypeException,
            InvalidMatrixLiteralException,
            WithStackTraceException
        ]
        for matrix_literal, exception in zip(matrix_literals, expected_exceptions):
            interpreter = Interpreter(None)
            with self.assertRaises(exception):
                interpreter.evaluate_matrix_literal(matrix_literal)


if __name__ == '__main__':
    unittest.main()
