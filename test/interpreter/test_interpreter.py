import unittest
import numpy as np

# noinspection PyProtectedMember
from execution.interpreter import Interpreter, _Variable, _VariableType, _FunctionStack
from execution.exception import *
from syntax_tree.constructions import *


class _ErrorObject:
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
            MatrixLiteral([_ErrorObject()], [])
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

    def test_dot_select_evaluation(self):
        """
        Tests dots select evaluation.
        """
        interpreter = Interpreter(None)
        dots_select = DotsSelect()
        expected_result = _Variable(_VariableType.DOTS, None)
        interpreter.evaluate_dots_select(dots_select)
        self.assertEqual(expected_result, interpreter.result)

    def test_identifier_without_indexing_evaluation(self):
        """
        Tests identifier evaluation WITHOUT using the index operator.

        Test cases are:
            - Identifier evaluates into number literal
            - Identifier evaluates into string literal
            - Identifier evaluates into matrix literal
        """
        inits = [
            {'i': _Variable(_VariableType.NUMBER, 42)},
            {'i': _Variable(_VariableType.STRING, 'Lorem ipsum')},
            {'i': _Variable(_VariableType.MATRIX, np.array([[1, 2, 3], [4, 5, 6]]))}
        ]
        is_same = [
            False,
            False,
            True
        ]
        identifier = Identifier('i')
        for init, same in zip(inits, is_same):
            interpreter = Interpreter(None)
            function_stack = _FunctionStack()
            function_stack.open_context(init)
            interpreter.stack = function_stack
            interpreter.evaluate_identifier(identifier)
            self.assertEqual(init['i'], interpreter.result)
            if same:
                self.assertIs(init['i'], interpreter.result)

    def test_identifier_with_indexing_evaluation(self):
        """
        Tests identifier evaluation WITH the usage of indexing operator.

        Test cases are:
            - [:, :]
            - [:, 0]
            - [0, :]
            - [0, 0]
        """
        init = {'i': _Variable(_VariableType.MATRIX, np.array([[1, 2, 3], [4, 5, 6]]))}
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        index_operators = [
            IndexOperator(DotsSelect(), DotsSelect()),
            IndexOperator(DotsSelect(), NumberLiteral(0)),
            IndexOperator(NumberLiteral(0), DotsSelect()),
            IndexOperator(NumberLiteral(0), NumberLiteral(0))
        ]
        expected_results = [
            init['i'],
            _Variable(_VariableType.MATRIX, np.array([[1, 4]])),
            _Variable(_VariableType.MATRIX, np.array([[1, 2, 3]])),
            _Variable(_VariableType.NUMBER, 1)
        ]
        is_same = [
            True,
            False,
            False,
            False
        ]
        for index, expected, same in zip(index_operators, expected_results, is_same):
            interpreter = Interpreter(None)
            interpreter.stack = function_stack
            interpreter.evaluate_identifier(Identifier('i', index))
            self.assertEqual(expected, interpreter.result)
            if same:
                self.assertIs(expected, interpreter.result)

    def test_invalid_identifier_with_indexing_evaluation(self):
        """
        Tests invalid identifier evaluation WITH the usage of indexing operator.

        Test cases are:
            - Invalid type of selector
            - Selector produces an exception
            - Out-of-range indexing
            - Indexing non-matrix object
        """
        init = {
            'i': _Variable(_VariableType.MATRIX, np.array([[1, 2, 3], [4, 5, 6]])),
            'j': _Variable(_VariableType.NUMBER, 42)
        }
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        index_operators = [
            IndexOperator(StringLiteral('Lorem ipsum'), DotsSelect()),
            IndexOperator(_ErrorObject(), NumberLiteral(0)),
            IndexOperator(NumberLiteral(10), NumberLiteral(12)),
            IndexOperator(NumberLiteral(0), NumberLiteral(0))
        ]
        errors = [
            InvalidTypeException,
            WithStackTraceException,
            IndexException,
            InvalidTypeException
        ]
        identifiers = [
            'i',
            'i',
            'i',
            'j'
        ]

        for index, error, identifier in zip(index_operators, errors, identifiers):
            interpreter = Interpreter(None)
            interpreter.stack = function_stack
            with self.assertRaises(error):
                interpreter.evaluate_identifier(Identifier(identifier, index))


if __name__ == '__main__':
    unittest.main()
