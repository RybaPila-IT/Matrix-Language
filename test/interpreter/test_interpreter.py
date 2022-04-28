import unittest
import numpy as np

# noinspection PyProtectedMember
from execution.interpreter import Interpreter, _Variable, _VariableType, _FunctionStack
from execution.exception import *
from syntax_tree.constructions import *


class _ErrorObject:
    def accept(self, visitor):
        raise WithStackTraceException()


class _Evaluator:
    def __init__(self, value):
        self.visited = False
        self.value = value

    def accept(self, visitor):
        self.visited = True
        # Simulate evaluation of the object by setting the result
        # in interpreter visitor object.
        visitor.result = self.value


class _VisitCounter:
    def __init__(self):
        self.count = 0

    def accept(self, _):
        self.count += 1


class _CountEvaluator:
    def __init__(self, count):
        self.count = count

    def accept(self, visitor):
        # Simulate some condition evaluation.
        visitor.result = self.count > 0
        self.count = max(0, self.count - 1)


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
        interpreter = Interpreter(None)
        # Start of test cases.
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
        interpreter = Interpreter(None)
        # Start of test cases.
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
        interpreter = Interpreter(None)
        # Start of test cases.
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
        interpreter = Interpreter(None)
        interpreter.stack = function_stack
        # Start of test cases.
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
        interpreter = Interpreter(None)
        interpreter.stack = function_stack
        # Start of test cases.
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
            with self.assertRaises(error):
                interpreter.evaluate_identifier(Identifier(identifier, index))

    def test_no_operator_relational_condition_evaluation(self):
        """
        Tests relation conditions evaluation.

        Test cases are:
            - Matrix evaluation.
            - Number evaluation.
            - String evaluation.
        """
        init = {
            'i': _Variable(_VariableType.MATRIX, np.array([0, 0, 0])),
            'j': _Variable(_VariableType.MATRIX, np.array([1, 2, 3])),
            'k': _Variable(_VariableType.NUMBER, 0),
            'l': _Variable(_VariableType.NUMBER, 42),
            'm': _Variable(_VariableType.STRING, ''),
            'n': _Variable(_VariableType.STRING, 'Lorem ipsum')
        }
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        interpreter = Interpreter(None)
        interpreter.stack = function_stack
        # Start of test cases.
        expected_results = [
            False,
            True,
            False,
            True,
            False,
            True
        ]
        identifiers = [
            'i',
            'j',
            'k',
            'l',
            'm',
            'n'
        ]

        for expected, identifier in zip(expected_results, identifiers):
            interpreter.evaluate_relation_condition(RelationCondition(False, Identifier(identifier)))
            self.assertEqual(expected, interpreter.result)

    def test_negation_relational_condition_evaluation(self):
        """
        Tests negation evaluation while evaluating relational conditions.

        Test cases are:
            - Negating True result
            - Negating False result
        """
        init = {
            'i': _Variable(_VariableType.MATRIX, np.array([0, 0, 0])),
            'j': _Variable(_VariableType.MATRIX, np.array([1, 2, 3]))
        }
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        interpreter = Interpreter(None)
        interpreter.stack = function_stack
        # Start of test cases.
        expected_results = [
            True,
            False
        ]
        identifiers = [
            'i',
            'j'
        ]

        for expected, identifier in zip(expected_results, identifiers):
            interpreter.evaluate_relation_condition(RelationCondition(True, Identifier(identifier)))
            self.assertEqual(expected, interpreter.result)

    def test_invalid_no_operator_relational_condition_evaluation(self):
        """
        Tests invalid relation conditions parsing WITHOUT operator usage.

        Test cases are:
            - Relation conditions evaluates with error
            - Result is obtained is of UNDEFINED type
        """
        init = {
            'i': _Variable(_VariableType.UNDEFINED, None),
        }
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        interpreter = Interpreter(None)
        interpreter.stack = function_stack
        # Start of test cases.
        rel_conditions = [
            RelationCondition(False, _ErrorObject()),
            RelationCondition(False, Identifier('i'))
        ]
        errors = [
            WithStackTraceException,
            InvalidTypeException
        ]

        for rel_condition, error in zip(rel_conditions, errors):
            with self.assertRaises(error):
                interpreter.evaluate_relation_condition(rel_condition)

    def test_operator_relation_condition_evaluation(self):
        """
        Tests relation condition evaluation WITH operator usage.

        Test cases are:
            - All matrix comparisons
            - All number comparisons
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        rel_conditions = [
            # Matrix tests.
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '<',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '>',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '>=',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(2)], []), '>=',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '<=',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '<=',
                              MatrixLiteral([NumberLiteral(1)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '==',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '==',
                              MatrixLiteral([NumberLiteral(1)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(1)], []), '!=',
                              MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, MatrixLiteral([NumberLiteral(2)], []), '!=',
                              MatrixLiteral([NumberLiteral(2)], [])),
            # Number tests.
            RelationCondition(False, NumberLiteral(1), '<', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(1), '>', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(1), '>=', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(2), '>=', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(1), '<=', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(1), '<=', NumberLiteral(1)),
            RelationCondition(False, NumberLiteral(1), '==', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(1), '==', NumberLiteral(1)),
            RelationCondition(False, NumberLiteral(1), '!=', NumberLiteral(2)),
            RelationCondition(False, NumberLiteral(2), '!=', NumberLiteral(2)),
        ]
        expected_results = [
            # Matrix results.
            True,
            False,
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            False,
            # Number tests.
            True,
            False,
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            False
        ]

        for rel_condition, expected in zip(rel_conditions, expected_results):
            interpreter.evaluate_relation_condition(rel_condition)
            self.assertEqual(expected, interpreter.result)

    def test_invalid_operator_relation_condition_evaluation(self):
        """
        Tests invalid relation condition evaluation WITH operator usage.

        Test cases are:
            - Error while right expression evaluation
            - Comparing objects type mismatch
            - Invalid object type for comparison
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        rel_conditions = [
            RelationCondition(False, NumberLiteral(2), '>', _ErrorObject()),
            RelationCondition(False, NumberLiteral(2), '==', MatrixLiteral([NumberLiteral(2)], [])),
            RelationCondition(False, NumberLiteral(2), '<', StringLiteral('Lorem ipsum')),
            RelationCondition(False, StringLiteral('Lorem ipsum'), '<', NumberLiteral(2))
        ]
        errors = [
            WithStackTraceException,
            TypesMismatchException,
            InvalidTypeException,
            InvalidTypeException
        ]

        for rel_condition, error in zip(rel_conditions, errors):
            with self.assertRaises(error):
                interpreter.evaluate_relation_condition(rel_condition)

    def test_and_condition_evaluation(self):
        """
        Tests and conditions evaluation.

        Test cases are:
            - All conditions evaluate to True.
            - Some condition evaluates to False.
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        and_conditions = [
            AndCondition([_Evaluator(True), _Evaluator(True), _Evaluator(True)]),
            AndCondition([_Evaluator(True), _Evaluator(False), _Evaluator(True)])
        ]
        evaluator_visited_states = [
            [True, True, True],
            [True, True, False]
        ]

        for and_condition, states in zip(and_conditions, evaluator_visited_states):
            interpreter.evaluate_and_condition(and_condition)
            for e, state in zip(and_condition.rel_conditions, states):
                self.assertEqual(state, e.visited)

    def test_invalid_and_condition_evaluation(self):
        """
        Tests invalid and condition evaluation.

        Test case is relation condition evaluation resulting in error.
        """
        interpreter = Interpreter(None)
        and_condition = AndCondition([_ErrorObject()])
        with self.assertRaises(WithStackTraceException):
            interpreter.evaluate_and_condition(and_condition)

    def test_or_condition_evaluation(self):
        """
        Tests or conditions evaluation.

        Test cases are:
            - All conditions evaluate to False.
            - Some condition evaluates to True.
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        or_conditions = [
            OrCondition([_Evaluator(False), _Evaluator(False), _Evaluator(False)]),
            OrCondition([_Evaluator(False), _Evaluator(True), _Evaluator(False)])
        ]
        evaluator_visited_states = [
            [True, True, True],
            [True, True, False]
        ]

        for or_condition, states in zip(or_conditions, evaluator_visited_states):
            interpreter.evaluate_or_condition(or_condition)
            for e, state in zip(or_condition.and_conditions, states):
                self.assertEqual(state, e.visited)

    def test_invalid_or_condition_evaluation(self):
        """
        Tests invalid or condition evaluation.

        Test case is and condition evaluation resulting in error.
        """
        interpreter = Interpreter(None)
        or_condition = OrCondition([_ErrorObject()])
        with self.assertRaises(WithStackTraceException):
            interpreter.evaluate_or_condition(or_condition)

    def test_negated_atomic_expression_evaluation(self):
        """
        Tests negated atomic expression evaluation.

        Test cases are:
            - Matrix negation.
            - Number negation.
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        negated_atomic_expressions = [
            NegatedAtomicExpression(MatrixLiteral([NumberLiteral(42), NumberLiteral(12)], [','])),
            NegatedAtomicExpression(NumberLiteral(42))
        ]
        expected_results = [
            _Variable(_VariableType.MATRIX, np.array([[-42, -12]])),
            _Variable(_VariableType.NUMBER, -42)
        ]

        for negated_atomic_expr, expected in zip(negated_atomic_expressions, expected_results):
            interpreter.evaluate_negated_atomic_expression(negated_atomic_expr)
            self.assertEqual(expected, interpreter.result)

    def test_invalid_negated_atomic_expression_evaluation(self):
        """
        Tests invalid negated atomic expression evaluation.

        Test cases are:
            - Invalid type of atomic expression evaluation
            - Atomic expression evaluation error
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        negated_atomic_expressions = [
            NegatedAtomicExpression(StringLiteral('Lorem ipsum')),
            NegatedAtomicExpression(_ErrorObject())
        ]
        errors = [
            InvalidTypeException,
            WithStackTraceException
        ]

        for negated_Atomic_expr, error in zip(negated_atomic_expressions, errors):
            with self.assertRaises(error):
                interpreter.evaluate_negated_atomic_expression(negated_Atomic_expr)

    def test_multiplicative_expression_evaluation(self):
        """
        Tests multiplicative expressions evaluation.

        Test cases are:
            - Numbers multiplication and division
            - Matrix multiplication
            - Matrix by number multiplication and division
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        mul_expressions = [
            MultiplicativeExpression([NumberLiteral(42), NumberLiteral(12)], ['*']),
            MultiplicativeExpression([NumberLiteral(42), NumberLiteral(2)], ['/']),
            MultiplicativeExpression([
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ';', ',']
                ),
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ';', ',']
                )], ['*']
            ),
            MultiplicativeExpression([
                MatrixLiteral([NumberLiteral(1), NumberLiteral(2)], [',']), NumberLiteral(2)], ['*']
            ),
            MultiplicativeExpression([
                MatrixLiteral([NumberLiteral(1), NumberLiteral(2)], [',']), NumberLiteral(2)], ['/']
            )
        ]
        expected_results = [
            _Variable(_VariableType.NUMBER, 504),
            _Variable(_VariableType.NUMBER, 21),
            _Variable(_VariableType.MATRIX, np.array([[7, 10], [15, 22]])),
            _Variable(_VariableType.MATRIX, np.array([[2, 4]])),
            _Variable(_VariableType.MATRIX, np.array([[.5, 1]]))
        ]

        for mul_expression, expected in zip(mul_expressions, expected_results):
            interpreter.evaluate_multiplicative_expression(mul_expression)
            self.assertEqual(expected, interpreter.result)

    def test_invalid_multiplicative_expression_evaluation(self):
        """
        Tests invalid multiplicative expressions evaluation.

        Test cases are:
            - Atomic expression results in error
            - Atomic expression evaluates into string
            - Atomic expression evaluates into undefined
            - Number * Matrix
            - Matrix dimensions mismatch while multiplying
            - Matrix / Matrix
            - Division by 0
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        mul_expressions = [
            MultiplicativeExpression([NumberLiteral(42), _ErrorObject()], ['*']),
            MultiplicativeExpression([NumberLiteral(42), StringLiteral('Lorem ipsum')], ['/']),
            MultiplicativeExpression([NumberLiteral(42), Identifier('i')], ['/']),
            MultiplicativeExpression([
                NumberLiteral(42),
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ';', ',']
                )], ['*']
            ),
            MultiplicativeExpression([
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3),
                     NumberLiteral(4), NumberLiteral(5), NumberLiteral(6)], [',', ',', ';', ',', ',']
                ),
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ';', ',']
                )], ['*']
            ),
            MultiplicativeExpression([
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ';', ',']
                ),
                MatrixLiteral(
                    [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3), NumberLiteral(4)], [',', ';', ',']
                )], ['/']
            ),
            MultiplicativeExpression([NumberLiteral(12), NumberLiteral(0)], ['/'])
        ]
        errors = [
            WithStackTraceException,
            TypesMismatchException,
            UndefinedVariableException,
            TypesMismatchException,
            MatrixDimensionsMismatchException,
            TypesMismatchException,
            ZeroDivisionException
        ]

        for mul_expression, error in zip(mul_expressions, errors):
            with self.assertRaises(error):
                interpreter.evaluate_multiplicative_expression(mul_expression)

    def test_additive_expression_evaluation(self):
        """
        Tests additive expressions evaluation.

        Test cases are:
            - Number add and subtract
            - Matrix add and subtract
            - Matrix +/- Number
        """
        interpreter = Interpreter(None)
        add_expressions = [
            AdditiveExpression([NumberLiteral(42), NumberLiteral(12)], ['+']),
            AdditiveExpression([NumberLiteral(42), NumberLiteral(12)], ['-']),
            AdditiveExpression([
                MatrixLiteral([NumberLiteral(12), NumberLiteral(42)], [',']),
                MatrixLiteral([NumberLiteral(2), NumberLiteral(2)], [','])
            ], ['+']),
            AdditiveExpression([
                MatrixLiteral([NumberLiteral(12), NumberLiteral(42)], [',']),
                MatrixLiteral([NumberLiteral(2), NumberLiteral(2)], [','])
            ], ['-']),
            AdditiveExpression([MatrixLiteral([NumberLiteral(12), NumberLiteral(42)], [',']), NumberLiteral(1)], ['+']),
            AdditiveExpression([MatrixLiteral([NumberLiteral(12), NumberLiteral(42)], [',']), NumberLiteral(1)], ['-']),
        ]
        expected_results = [
            _Variable(_VariableType.NUMBER, 54),
            _Variable(_VariableType.NUMBER, 30),
            _Variable(_VariableType.MATRIX, np.array([[14, 44]])),
            _Variable(_VariableType.MATRIX, np.array([[10, 40]])),
            _Variable(_VariableType.MATRIX, np.array([[13, 43]])),
            _Variable(_VariableType.MATRIX, np.array([[11, 41]]))
        ]

        for add_expression, expected in zip(add_expressions, expected_results):
            interpreter.evaluate_additive_expression(add_expression)
            self.assertEqual(expected, interpreter.result)

    def test_invalid_additive_expression_evaluation(self):
        """
        Tests invalid additive expressions evaluation.

        Test cases are:
            - Mul expression results in error
            - Mul expression evaluates into string
            - Mul expression evaluates into undefined
        """
        interpreter = Interpreter(None)
        # Start of test cases.
        add_expressions = [
            AdditiveExpression([NumberLiteral(42), _ErrorObject()], ['*']),
            AdditiveExpression([NumberLiteral(42), StringLiteral('Lorem ipsum')], ['/']),
            AdditiveExpression([NumberLiteral(42), Identifier('i')], ['/'])
        ]
        errors = [
            WithStackTraceException,
            TypesMismatchException,
            UndefinedVariableException
        ]

        for add_expression, error in zip(add_expressions, errors):
            with self.assertRaises(error):
                interpreter.evaluate_additive_expression(add_expression)

    def test_no_indexing_assign_statement_evaluation(self):
        """
        Tests assign statement evaluation WITHOUT usage of indexing operator.

        Test cases are:
            - Assigning the Number to defined variable
            - Assigning the Number to undefined variable
            - Assigning the String to defined variable
            - Assigning the String to undefined variable
            - Assigning the Matrix to defined variable
            - Assigning the Matrix to undefined variable
        """
        interpreter = Interpreter(None)
        inits = [
            {'i': _Variable(_VariableType.NUMBER, 24)},
            {'i': _Variable(_VariableType.STRING, 'Lorem ipsum')},
            {'i': _Variable(_VariableType.MATRIX, np.array([[1, 2, 3]]))}
        ]
        assign_statements = [
            (
                AssignStatement(Identifier('i'), NumberLiteral(42)),
                AssignStatement(Identifier('j'), NumberLiteral(42))
            ),
            (
                AssignStatement(Identifier('i'), StringLiteral('Hello world!')),
                AssignStatement(Identifier('j'), StringLiteral('Hello world!'))
            ),
            (
                AssignStatement(Identifier('i'), MatrixLiteral([NumberLiteral(12)], [])),
                AssignStatement(Identifier('j'), MatrixLiteral([NumberLiteral(12)], []))
            )
        ]
        expected_results = [
            _Variable(_VariableType.NUMBER, 42),
            _Variable(_VariableType.STRING, 'Hello world!'),
            _Variable(_VariableType.MATRIX, np.array([[12]]))
        ]

        for init, assign_statement_pair, expected in zip(inits, assign_statements, expected_results):
            function_stack = _FunctionStack()
            function_stack.open_context(init)
            interpreter.stack = function_stack
            interpreter.evaluate_assign_statement(assign_statement_pair[0])
            self.assertEqual(expected, init[assign_statement_pair[0].identifier.name])
            interpreter.evaluate_assign_statement(assign_statement_pair[1])
            self.assertEqual(expected, init[assign_statement_pair[1].identifier.name])

    def test_invalid_no_indexing_assign_statement_evaluation(self):
        """
        Tests invalid assign statement evaluation WITHOUT usage of indexing operator.

        Test case is types mismatch for Matrix and Number.
        """
        init = {
            'i': _Variable(_VariableType.MATRIX, np.array([[12, 42]]))
        }
        assign_statement = AssignStatement(Identifier('i'), NumberLiteral(12))
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        interpreter = Interpreter(None)
        interpreter.stack = function_stack
        with self.assertRaises(TypesMismatchException):
            interpreter.evaluate_assign_statement(assign_statement)

    def test_indexing_assign_statement_evaluation(self):
        """
        Tests assign statement evaluation WITH usage of indexing operator.

        Test cases are:
            - Assigning single number
            - Assigning row
            - Assigning column
            - Assigning all matrix values
        """
        interpreter = Interpreter(None)
        init = {
            'i': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
            'j': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
            'k': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
            'l': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
        }
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        interpreter.stack = function_stack
        assign_statements = [
            AssignStatement(
                Identifier('i', IndexOperator(NumberLiteral(0), NumberLiteral(0))),
                NumberLiteral(42)
            ),
            AssignStatement(
                Identifier('j', IndexOperator(NumberLiteral(0), DotsSelect())),
                MatrixLiteral([NumberLiteral(12), NumberLiteral(42)], [','])
            ),
            AssignStatement(
                Identifier('k', IndexOperator(DotsSelect(), NumberLiteral(0))),
                MatrixLiteral([NumberLiteral(12), NumberLiteral(42)], [','])
            ),
            AssignStatement(
                Identifier('l', IndexOperator(DotsSelect(), DotsSelect())),
                MatrixLiteral(
                    [NumberLiteral(12), NumberLiteral(42), NumberLiteral(12), NumberLiteral(42)],
                    [',', ';', ','])
            ),
        ]
        expected_results = [
            _Variable(_VariableType.MATRIX, np.array([[42, 2], [3, 4]])),
            _Variable(_VariableType.MATRIX, np.array([[12, 42], [3, 4]])),
            _Variable(_VariableType.MATRIX, np.array([[12, 2], [42, 4]])),
            _Variable(_VariableType.MATRIX, np.array([[12, 42], [12, 42]]))
        ]
        identifiers = [
            'i',
            'j',
            'k',
            'l'
        ]

        for assign_statement, expected, ident in zip(assign_statements, expected_results, identifiers):
            interpreter.evaluate_assign_statement(assign_statement)
            self.assertEqual(expected, interpreter.stack.get_variable(ident))

    def test_invalid_indexing_assign_statement_evaluation(self):
        """
        Tests invalid assign statement evaluation WITH usage of indexing operator.

        Test cases are:
            - Indexing not a Matrix
            - Assigning String
            - Mismatch of vector assigned
            - Selectors evaluation error
        """
        interpreter = Interpreter(None)
        init = {
            'i': _Variable(_VariableType.NUMBER, 32),
            'j': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
            'k': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
            'l': _Variable(_VariableType.MATRIX, np.array([[1, 2], [3, 4]])),
        }
        function_stack = _FunctionStack()
        function_stack.open_context(init)
        interpreter.stack = function_stack
        assign_statements = [
            AssignStatement(
                Identifier('i', IndexOperator(NumberLiteral(0), NumberLiteral(0))),
                NumberLiteral(42)
            ),
            AssignStatement(
                Identifier('j', IndexOperator(NumberLiteral(0), NumberLiteral(0))),
                StringLiteral('Lorem ipsum')
            ),
            AssignStatement(
                Identifier('k', IndexOperator(DotsSelect(), NumberLiteral(0))),
                MatrixLiteral([NumberLiteral(12), NumberLiteral(42), NumberLiteral(36)], [',', ','])
            ),
            AssignStatement(
                Identifier('l', IndexOperator(_ErrorObject(), DotsSelect())),
                MatrixLiteral(
                    [NumberLiteral(12), NumberLiteral(42), NumberLiteral(12), NumberLiteral(42)],
                    [',', ';', ','])
            ),
        ]
        errors = [
            InvalidTypeException,
            InvalidTypeException,
            IndexException,
            WithStackTraceException
        ]

        for assign_statement, error in zip(assign_statements, errors):
            with self.assertRaises(error):
                interpreter.evaluate_assign_statement(assign_statement)

    def test_return_statement_evaluation(self):
        """
        Tests return statement evaluation.

        Test cases are:
            - Plain return
            - Return with value
        """
        interpreter = Interpreter(None)
        return_statements = [
            ReturnStatement(),
            ReturnStatement(NumberLiteral(42))
        ]
        expected_results = [
            _Variable(_VariableType.UNDEFINED, None),
            _Variable(_VariableType.NUMBER, 42)
        ]

        for return_statement, expected in zip(return_statements, expected_results):
            interpreter.returns = False
            interpreter.evaluate_return_statement(return_statement)
            self.assertEqual(expected, interpreter.result)
            self.assertEqual(True, interpreter.returns)

    def test_invalid_return_statement_evaluation(self):
        """
        Tests invalid return statement evaluation.

        Test case is expression evaluation resulting in error.
        """
        interpreter = Interpreter(None)
        return_statement = ReturnStatement(_ErrorObject())
        with self.assertRaises(WithStackTraceException):
            interpreter.evaluate_return_statement(return_statement)

    def test_if_statement_evaluation(self):
        """
        Tests if statement evaluation.

        Test cases are:
            - True condition and if block execution
            - False condition and no block execution
            - False condition and else block execution
        """
        interpreter = Interpreter(None)
        if_statements = [
            IfStatement(_Evaluator(True), _VisitCounter()),
            IfStatement(_Evaluator(False), _VisitCounter()),
            IfStatement(_Evaluator(True), _VisitCounter(), _VisitCounter()),
            IfStatement(_Evaluator(False), _VisitCounter(), _VisitCounter())
        ]
        expected_results = [
            (1, None),
            (0, None),
            (1, 0),
            (0, 1)
        ]

        for if_statement, expected in zip(if_statements, expected_results):
            interpreter.evaluate_if_statement(if_statement)
            self.assertEqual(True, if_statement.condition.visited)
            self.assertEqual(expected[0], if_statement.statement_block.count)
            if expected[1] is not None:
                self.assertEqual(expected[1], if_statement.else_statement.count)

    def test_until_statement_evaluation(self):
        """
        Tests until statement evaluation.

        Test cases are:
            - No loop execution
            - 1 time loop execution
            - Multiple times loop execution
        """
        interpreter = Interpreter(None)
        until_statements = [
            UntilStatement(_CountEvaluator(0), _VisitCounter()),
            UntilStatement(_CountEvaluator(1), _VisitCounter()),
            UntilStatement(_CountEvaluator(42), _VisitCounter()),
        ]
        expected_results = [
            0,
            1,
            42
        ]

        for until_statement, expected in zip(until_statements, expected_results):
            interpreter.evaluate_until_statement(until_statement)
            self.assertEqual(0, until_statement.condition.count)
            self.assertEqual(expected, until_statement.statement_block.count)


if __name__ == '__main__':
    unittest.main()
