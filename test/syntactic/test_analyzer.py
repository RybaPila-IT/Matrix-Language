import unittest
from syntax_tree.constructions import *
from syntactic.analyzer import SyntacticAnalyzer
from syntactic.exception import *
from lexical.analyzer import LexicalAnalyzer
from data.source.pipeline import positional_string_source_pipe


def syntactic_analyzer_pipeline(content):
    return SyntacticAnalyzer(
        LexicalAnalyzer(
            positional_string_source_pipe(content)
        )
    )


class TestSyntacticAnalyzer(unittest.TestCase):

    def test_parameters_parsing(self):
        """
        Testing parameters parsing by syntactic analyzer.

        Test cases are:
           - no parameter.
           - single parameter.
           - multiple parameters.
        """
        contents = [
            ')',
            'arg1)',
            'arg1, arg2, arg3)'
        ]
        expected_constructions = [
            [],
            [Identifier('arg1')],
            [Identifier('arg1'), Identifier('arg2'), Identifier('arg3')]
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_parameters()
            self.assertEqual(expected, result)

    def test_invalid_parameters_parsing(self):
        """
        Testing invalid parameters parsing by syntactic analyzer.

        Test case is:
            - missing identifier after comma.
        """
        content = 'arg1, arg2,)'
        parser = syntactic_analyzer_pipeline(content)
        with self.assertRaises(MissingIdentifierException):
            # noinspection PyUnresolvedReferences
            parser._SyntacticAnalyzer__try_parse_parameters()

    def test_simple_literals_parsing(self):
        """
        Testing string and number literals parsing by syntactic analyzer.

        Test cases are:
            - No valid literal.
            - String literal.
            - Number literal.
        """
        contents = [
            'main()',
            '"$"My string$""',
            '1234'
        ]
        expected_constructions = [
            None,
            StringLiteral('"My string"'),
            NumberLiteral(1234)
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_literal()
            self.assertEqual(expected, result)

    def test_relation_condition_parsing(self):
        """
        Testing relation conditions parsing by syntactic analyzer.

        Test cases are:
            - a
            - ! a
            - a <= b
            - ! (a+20) >= (b*d)
        """
        contents = [
            'a',
            '! a',
            'a <= b',
            '! (a+20) >= (b*d)',
        ]
        expected_constructions = [
            Identifier('a'),
            RelationCondition(
                True,
                Identifier('a')
            ),
            RelationCondition(
                False,
                Identifier('a'),
                '<=',
                Identifier('b')
            ),
            RelationCondition(
                True,
                AdditiveExpression(
                    [Identifier('a'), NumberLiteral(20)],
                    ['+']
                ),
                '>=',
                MultiplicativeExpression(
                    [Identifier('b'), Identifier('d')],
                    ['*']
                )
            )
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_relation_condition()
            self.assertEqual(expected, result)

    def test_invalid_relation_condition_parsing(self):
        """
        Testing invalid relation conditions parsing by syntactic analyzer.

        Test cases are:
            - !! a
            - a < ! a
            - a == :
        """
        contents = [
            '!! a',
            ' a < ! a'
            'a == :',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(MissingExpressionException):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_relation_condition()

    def test_and_condition_parsing(self):
        """
        Testing and conditions parsing by syntactic analyzer.

        Test cases are:
            - a
            - a and b and c
            - (a+b > 0) and (12 >= 12)
            - (a and b) and c and d
        """
        contents = [
            'a',
            'a and b and c',
            '(a+b > 0) and (12 >= 12)',
            '(a and b) and c and d'
        ]
        expected_constructions = [
            Identifier('a'),
            AndCondition([
                Identifier('a'),
                Identifier('b'),
                Identifier('c')
            ]),
            AndCondition([
                RelationCondition(
                    False,
                    AdditiveExpression([Identifier('a'), Identifier('b')], ['+']),
                    '>',
                    NumberLiteral(0)
                ),
                RelationCondition(
                    False,
                    NumberLiteral(12),
                    '>=',
                    NumberLiteral(12)
                )
            ]),
            AndCondition([
                AndCondition([
                    Identifier('a'),
                    Identifier('b')
                ]),
                Identifier('c'),
                Identifier('d')
            ])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_and_condition()
            self.assertEqual(expected, result)

    def test_invalid_and_condition_parsing(self):
        """
        Testing invalid and conditions parsing by syntactic analyzer.

        Test cases are:
            - a and b and
            - a and if (1 > 2) {return false} and c
        """
        contents = [
            'a and b and',
            'a and if (1 > 2) {return false} and c',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(MissingConditionException):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_and_condition()

    def test_or_condition_parsing(self):
        """
        Testing or conditions parsing by syntactic analyzer.

        Test cases are:
            - a
            - a or b or c
            - (a+b > 0) or (12 >= 12)
            - (a or b) or c or d
        """
        contents = [
            'a',
            'a or b or c',
            '(a+b > 0) or (12 >= 12)',
            '(a or b) or c or d'
        ]
        expected_constructions = [
            Identifier('a'),
            OrCondition([
                Identifier('a'),
                Identifier('b'),
                Identifier('c')
            ]),
            OrCondition([
                RelationCondition(
                    False,
                    AdditiveExpression([Identifier('a'), Identifier('b')], ['+']),
                    '>',
                    NumberLiteral(0)
                ),
                RelationCondition(
                    False,
                    NumberLiteral(12),
                    '>=',
                    NumberLiteral(12)
                )
            ]),
            OrCondition([
                OrCondition([
                    Identifier('a'),
                    Identifier('b')
                ]),
                Identifier('c'),
                Identifier('d')
            ])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_or_condition()
            self.assertEqual(expected, result)

    def test_invalid_or_condition_parsing(self):
        """
        Testing invalid or conditions parsing by syntactic analyzer.

        Test cases are:
            - a or b or
            - a or if (1 > 2) {return false} or c
        """
        contents = [
            'a or b or',
            'a or if (1 > 2) {return false} or c',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(MissingConditionException):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_or_condition()

    def test_atomic_expression_parsing(self):
        """
        Testing atomic expressions parsing by syntactic analyzer.

        Test cases are:
            - a
            - - a
            - - (-a)
        """
        contents = [
            'a',
            '- a',
            '- (-a)'
        ]
        expected_constructions = [
            Identifier('a'),
            NegatedAtomicExpression(Identifier('a')),
            NegatedAtomicExpression(NegatedAtomicExpression(Identifier('a')))
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_atomic_expression()
            self.assertEqual(expected, result)

    def test_invalid_atomic_expression_parsing(self):
        """
        Testing invalid atomic expressions parsing by syntactic analyzer.

        Test cases are:
            - - if (1 >2) {return false}
            - - -a
            - -({a})
        """
        contents = [
            '- if (1 > 2) {return false}',
            '- - a',
            '-({a})',
        ]
        errors = [
            MissingExpressionException,
            MissingExpressionException,
            MissingConditionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_atomic_expression()

    def test_multiplicative_expression_parsing(self):
        """
        Testing multiplicative expressions parsing by syntactic analyzer.

        Test cases are:
            - a
            - a * b / c
            - (a * (a / b)) * c / 12
        """
        contents = [
            'a',
            'a * b / c',
            '(a * (a / b)) * c / 12'
        ]
        expected_constructions = [
            # Test 1.
            Identifier('a'),
            # Test 2.
            MultiplicativeExpression([
                Identifier('a'),
                Identifier('b'),
                Identifier('c')
            ], ['*', '/']),
            # Test 3.
            MultiplicativeExpression([
                MultiplicativeExpression([
                    Identifier('a'),
                    MultiplicativeExpression([
                        Identifier('a'),
                        Identifier('b')
                    ], ['/'])
                ], ['*']),
                Identifier('c'),
                NumberLiteral(12)
            ], ['*', '/'])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_multiplicative_expression()
            self.assertEqual(expected, result)

    def test_invalid_multiplicative_expression_parsing(self):
        """
        Testing invalid multiplicative expressions parsing by syntactic analyzer.

        Test cases are:
            - 12 *
            - (12 * ) / 34
            - 34 * (if (1 > 2) {return false})
        """
        contents = [
            '12 *',
            '(12 * ) / 34',
            '34 * (if (1 > 2) {return false})'
        ]
        errors = [
            MissingExpressionException,
            MissingExpressionException,
            MissingConditionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_multiplicative_expression()

    def test_additive_expression_parsing(self):
        """
        Testing additive expressions parsing by syntactic analyzer.

        Test cases are:
            - a
            - a + b - c
            - (a + (a - b)) - c + 12
            - (a*b) + c/d
        """
        contents = [
            'a',
            'a + b - c',
            '(a + (a - b)) - c + 12',
            '(a*b) + c/d'
        ]
        expected_constructions = [
            # Test 1.
            Identifier('a'),
            # Test 2.
            AdditiveExpression([
                Identifier('a'),
                Identifier('b'),
                Identifier('c')
            ], ['+', '-']),
            # Test 3.
            AdditiveExpression([
                AdditiveExpression([
                    Identifier('a'),
                    AdditiveExpression([
                        Identifier('a'),
                        Identifier('b')
                    ], ['-'])
                ], ['+']),
                Identifier('c'),
                NumberLiteral(12)
            ], ['-', '+']),
            # Test 4.
            AdditiveExpression([
                MultiplicativeExpression([
                    Identifier('a'),
                    Identifier('b')
                ], ['*']),
                MultiplicativeExpression([
                    Identifier('c'),
                    Identifier('d')
                ], ['/'])
            ], ['+'])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_additive_expression()
            self.assertEqual(expected, result)

    def test_invalid_additive_expression_parsing(self):
        """
        Testing invalid additive expressions parsing by syntactic analyzer.

        Test cases are:
            - 12 -
            - (12 + ) - 34
            - 34 + (if (1 > 2) {return false})
        """
        contents = [
            '12 -',
            '(12 + ) - 34',
            '34 + (if (1 > 2) {return false})'
        ]
        errors = [
            MissingExpressionException,
            MissingExpressionException,
            MissingConditionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_additive_expression()

    def test_matrix_literal_parsing(self):
        """
        Testing matrix literals parsing by syntactic analyzer.

        Test cases are:
            - [ 1 ]
            - [ 1, 2; 3, 4 ]
            - [ 1 + 2; a * c ]
        """
        contents = [
            '[ 1 ]',
            '[ 1, 2; 3, 4 ]',
            '[ 1 + 2; a * c ]'
        ]
        expected_constructions = [
            # Test 1.
            MatrixLiteral([
                NumberLiteral(1)
            ], []),
            # Test 2.
            MatrixLiteral([
                NumberLiteral(1),
                NumberLiteral(2),
                NumberLiteral(3),
                NumberLiteral(4)
            ], [',', ';', ',']),
            # Test 3.
            MatrixLiteral([
                AdditiveExpression([
                    NumberLiteral(1),
                    NumberLiteral(2)
                ], ['+']),
                MultiplicativeExpression([
                    Identifier('a'),
                    Identifier('c')
                ], ['*'])
            ], [';'])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_matrix_literal()
            self.assertEqual(expected, result)

    def test_invalid_matrix_literal_parsing(self):
        """
        Testing invalid matrix literals parsing by syntactic analyzer.

        Test cases are:
            - [1; a
            - [ {a}, b ]
            - [ a; : ]
            - [ a; ]
        """
        contents = [
            '[1; a ',
            '[ {a}, b ] ',
            '[ a; : ]',
            '[ a; ]'
        ]
        errors = [
            MissingBracketException,
            MissingExpressionException,
            MissingExpressionException,
            MissingExpressionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_matrix_literal()

    def test_index_operator_parsing(self):
        """
        Testing index operators parsing by syntactic analyzer.

        Test cases are:
            - [ 0, 0 ]
            - [ a + b, c * d]
            - [ :, :]
        """
        contents = [
            '[ 0, 0 ]',
            '[ a + b, c * d ]',
            '[ :, : ]'
        ]
        expected_constructions = [
            # Test 1.
            IndexOperator(
                NumberLiteral(0),
                NumberLiteral(0)
            ),
            # Test 2.
            IndexOperator(
                AdditiveExpression([
                    Identifier('a'),
                    Identifier('b')
                ], ['+']),
                MultiplicativeExpression([
                    Identifier('c'),
                    Identifier('d')
                ], ['*'])
            ),
            # Test 3.
            IndexOperator(
                DotsSelect(),
                DotsSelect()
            )
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_index_operator()
            self.assertEqual(expected, result)

    def test_invalid_index_operator_parsing(self):
        """
         Testing invalid index operators parsing by syntactic analyzer.

         Test cases are:
             - [1, ]
             - [ 1 1 ]
             - [1, 1
             - [ {1}, 1 ]
             - [ : , :, : ]
         """
        contents = [
            '[1, ]',
            '[ 1 1 ]',
            '[1, 1',
            '[ {1}, 1 ]',
            '[ : , :, : ]'
        ]
        errors = [
            MissingSelectorException,
            UnexpectedTokenException,
            MissingBracketException,
            MissingSelectorException,
            MissingBracketException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_index_operator()

    def test_function_call_parsing(self):
        """
        Testing function calls parsing by syntactic analyzer.

        Test cases are:
            - main()
            - fun(a, 1, "hello")
            - fun(a+b, [ 1; 2 ], fun(1))
        """
        contents = [
            'main()',
            'fun(a, 1, "hello")',
            'fun(a+b, [ 1; 2 ], fun(1))',
        ]
        expected_constructions = [
            # Test 1.
            FunctionCall('main', []),
            # Test 2.
            FunctionCall('fun', [
                Identifier('a'),
                NumberLiteral(1),
                StringLiteral('hello')
            ]),
            # Test 3.
            FunctionCall('fun', [
                AdditiveExpression([Identifier('a'), Identifier('b')], ['+']),
                MatrixLiteral([NumberLiteral(1), NumberLiteral(2)], [';']),
                FunctionCall('fun', [NumberLiteral(1)])
            ])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_identifier_or_function_call()
            self.assertEqual(expected, result)

    def test_invalid_function_call_parsing(self):
        """
         Testing invalid function call parsing by syntactic analyzer.

         Test cases are:
             - main(
             - main(1,)
             - main(until)
             - main(:)
         """
        contents = [
            'main(',
            'main(1,)',
            'main(until)',
            'main(:)',
        ]
        errors = [
            MissingBracketException,
            MissingExpressionException,
            MissingBracketException,
            MissingBracketException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_identifier_or_function_call()

    def test_assign_statement_parsing(self):
        """
        Testing assign statements parsing by syntactic analyzer.

        Test cases are:
            - a = 12
            - a = a + 1
            - a = fun(12)
            - a[0, :] = [1, 2, 3]
        """
        contents = [
            'a = 12',
            'a = a + 1',
            'a = fun(12)',
            'a[0, :] = [1, 2, 3]'
        ]
        expected_constructions = [
            # Test 1.
            AssignStatement(Identifier('a'), NumberLiteral(12)),
            # Test 2.
            AssignStatement(Identifier('a'),
                            AdditiveExpression(
                                [Identifier('a'), NumberLiteral(1)],
                                ['+']
                            )
                            ),
            # Test 3.
            AssignStatement(Identifier('a'),
                            FunctionCall(
                                'fun',
                                [NumberLiteral(12)]
                            )
                            ),
            # Test 4.
            AssignStatement(Identifier('a', IndexOperator(NumberLiteral(0), DotsSelect())),
                            MatrixLiteral(
                                [NumberLiteral(1), NumberLiteral(2), NumberLiteral(3)],
                                [',', ',']
                            )
                            )
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_assignment_or_function_call()
            self.assertEqual(expected, result)

    def test_invalid_assign_statement_parsing(self):
        """
          Testing invalid assign statement parsing by syntactic analyzer.

          Test cases are:
              - a+b = 1
              - a = if (1>2) {return false}
              - a = :
          """
        contents = [
            'a+b = 1',
            'a = if (1>2) {return false}',
            'a = :',
        ]
        errors = [
            UnexpectedTokenException,
            MissingExpressionException,
            MissingExpressionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_assignment_or_function_call()

    def test_return_statement_parsing(self):
        """
        Testing return statement parsing by syntactic analyzer.

        Test cases are:
            - return
            - return fun(1)
            - return a + b
        """
        contents = [
            'return',
            'return fun(1)',
            'return a + b',
        ]
        expected_constructions = [
            # Test 1.
            ReturnStatement(),
            # Test 2.
            ReturnStatement(FunctionCall('fun', [NumberLiteral(1)])),
            # Test 3.
            ReturnStatement(AdditiveExpression([Identifier('a'), Identifier('b')], ['+']))
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_return_statement()
            self.assertEqual(expected, result)

    def test_if_statement_parsing(self):
        """
        Testing if statement parsing by syntactic analyzer.

        Test cases are:
            - if (1>2) {return 0}
            - if (a and c) {return 0} else {return 1}
            - if (a or c) {return 0} else if (2 > 1) {return 1} else {return a}
        """
        contents = [
            'if (1>2) {return 0}',
            'if (a and c) {return 0} else {return 1}',
            'if (a or c) {return 0} else if (! 2 > 1) {return 1} else {return a}',
        ]
        expected_constructions = [
            # Test 1.
            IfStatement(
                RelationCondition(False, NumberLiteral(1), '>', NumberLiteral(2)),
                StatementBlock([
                    ReturnStatement(NumberLiteral(0))
                ])
            ),
            # Test 2.
            IfStatement(
                AndCondition([Identifier('a'), Identifier('c')]),
                StatementBlock([
                    ReturnStatement(NumberLiteral(0)),
                ]),
                StatementBlock([
                    ReturnStatement(NumberLiteral(1)),
                ]),
            ),
            # Test 3.
            IfStatement(
                OrCondition([Identifier('a'), Identifier('c')]),
                StatementBlock([
                    ReturnStatement(NumberLiteral(0)),
                ]),
                IfStatement(
                    RelationCondition(True, NumberLiteral(2), '>', NumberLiteral(1)),
                    StatementBlock([
                        ReturnStatement(NumberLiteral(1)),
                    ]),
                    StatementBlock([
                        ReturnStatement(Identifier('a')),
                    ]),
                )

            )
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_if_statement()
            self.assertEqual(expected, result)

    def test_invalid_if_statement_parsing(self):
        """
          Testing invalid if statement parsing by syntactic analyzer.

          Test cases are:
              - if () {return 0}
              - if (a>b {return 0}
              - if (a>b) return 0
              - if (a>b) {a++}
              - if (if (a>b)) {return 0}
          """
        contents = [
            'if () {return 0}',
            'if (a>b {return 0}',
            'if (a>b) return 0',
            'if (a>b) {a++}',
            'if (if (a>b)) {return 0}'
        ]
        errors = [
            MissingConditionException,
            MissingBracketException,
            MissingStatementBlockException,
            UnexpectedTokenException,
            MissingConditionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_if_statement()

    def test_until_statement_parsing(self):
        """
         Testing until statement parsing by syntactic analyzer.

         Test cases are:
             - until (a <= 12) {a = a + 1}
             - until (a and c) {a = fun(a)}
         """
        contents = [
            'until (a <= 12) {a = a + 1}',
            'until (a and c) {a = fun(a)}',
        ]
        expected_constructions = [
            # Test 1.
            UntilStatement(
                RelationCondition(False, Identifier('a'), '<=', NumberLiteral(12)),
                StatementBlock([
                    AssignStatement(Identifier('a'), AdditiveExpression([Identifier('a'), NumberLiteral(1)], ['+']))
                ])
            ),
            # Test 2.
            UntilStatement(
                AndCondition([Identifier('a'), Identifier('c')]),
                StatementBlock([
                    AssignStatement(Identifier('a'), FunctionCall('fun', [Identifier('a')]))
                ])
            ),
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_until_statement()
            self.assertEqual(expected, result)

    def test_invalid_until_statement_parsing(self):
        """
          Testing invalid until statement parsing by syntactic analyzer.

          Test cases are:
              - until () {a = a + 1}
              - until (a>b {a = a + 1}
              - until (a>b) a = a + 1
              - until (a>b) {a++}
              - until (if (a>b)) {a = a + 1}
          """
        contents = [
            'until () {a = a + 1}',
            'until (a>b {a = a + 1}',
            'until (a>b) a = a + 1',
            'until (a>b) {a++}',
            'until (if (a>b)) {a = a + 1}'
        ]
        errors = [
            MissingConditionException,
            MissingBracketException,
            MissingStatementBlockException,
            UnexpectedTokenException,
            MissingConditionException
        ]
        # Starting the test.
        for content, error in zip(contents, errors):
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(error):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_until_statement()

    def test_statement_block_parsing(self):
        """
         Testing statement block parsing by syntactic analyzer.

         Test cases are:
             - { { {} } }
             - { a = a + 1 n = fun(a) }
             - { until (a <= 12) {a = a + 1} }
         """
        contents = [
            '{ { {} } }',
            '{ a = a + 1 n = fun(a) }',
            '{ until (a <= 12) {a = a + 1} }'
        ]
        expected_constructions = [
            # Test 1.
            StatementBlock([StatementBlock([StatementBlock([])])]),
            # Test 2.
            StatementBlock([
                AssignStatement(Identifier('a'), AdditiveExpression([Identifier('a'), NumberLiteral(1)], ['+'])),
                AssignStatement(Identifier('n'), FunctionCall('fun', [Identifier('a')]))
            ]),
            # Test 3.
            StatementBlock([
                UntilStatement(
                    RelationCondition(False, Identifier('a'), '<=', NumberLiteral(12)),
                    StatementBlock([
                        AssignStatement(Identifier('a'), AdditiveExpression([Identifier('a'), NumberLiteral(1)], ['+']))
                    ])
                ),
            ])
        ]
        # Starting the test.
        for content, expected in zip(contents, expected_constructions):
            parser = syntactic_analyzer_pipeline(content)
            # noinspection PyUnresolvedReferences
            result = parser._SyntacticAnalyzer__try_parse_statement_block()
            self.assertEqual(expected, result)

    def test_invalid_statement_block_parsing(self):
        """
          Testing invalid statement block parsing by syntactic analyzer.

          Test cases are:
              - { { { } }
              - {a++}
              - { -() }
          """
        contents = [
            '{ { { } }',
            '{a++}',
            '{ -() }',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_statement_block()

    def test_function_definition_parsing_1(self):
        """
        Testing function definition parsing by syntactic analyzer vol. 1.
        """
        content = """
            main() {
                i = 0
                until (i < 10) {
                    i = i + 1
                }
                print("i = ", i)
            }
        """
        expected = FunctionDefinition('main', [],
                                      StatementBlock([
                                          AssignStatement(Identifier('i'), NumberLiteral(0)),
                                          UntilStatement(
                                              RelationCondition(False, Identifier('i'), '<', NumberLiteral(10)),
                                              StatementBlock([
                                                  AssignStatement(Identifier('i'), AdditiveExpression([
                                                      Identifier('i'),
                                                      NumberLiteral(1)
                                                  ], ['+'])),
                                              ]),
                                          ),
                                          FunctionCall('print', [StringLiteral('i = '), Identifier('i')])
                                      ]))
        # Starting the test.
        parser = syntactic_analyzer_pipeline(content)
        # noinspection PyUnresolvedReferences
        result = parser._SyntacticAnalyzer__try_parse_function_definition()
        self.assertEqual(expected, result)

    def test_function_definition_parsing_2(self):
        """
        Testing function definition parsing by syntactic analyzer vol. 2.
        """
        content = """
            fib(n) {
                if (n == 1) {
                    return 1
                } 
                return fib(n-1)
            }
        """
        expected = FunctionDefinition('fib', [Identifier('n')],
                                      StatementBlock([
                                          IfStatement(
                                              RelationCondition(False, Identifier('n'), '==', NumberLiteral(1)),
                                              StatementBlock([
                                                  ReturnStatement(NumberLiteral(1))
                                              ]),
                                          ),
                                          ReturnStatement(
                                              FunctionCall('fib', [
                                                  AdditiveExpression([
                                                      Identifier('n'),
                                                      NumberLiteral(1)], ['-'])
                                              ])
                                          )
                                      ]))
        # Starting the test.
        parser = syntactic_analyzer_pipeline(content)
        # noinspection PyUnresolvedReferences
        result = parser._SyntacticAnalyzer__try_parse_function_definition()
        self.assertEqual(expected, result)

    def test_function_definition_parsing_3(self):
        """
        Testing function definition parsing by syntactic analyzer vol. 3.
        """
        content = """
                    rot90(matrix) {
                        rot = [  0, 1;
                                -1, 0 ]
                        return matrix * rot
                    }
                """
        expected = FunctionDefinition('rot90', [Identifier('matrix')],
                                      StatementBlock([
                                          AssignStatement(
                                              Identifier('rot'),
                                              MatrixLiteral([
                                                  NumberLiteral(0),
                                                  NumberLiteral(1),
                                                  NegatedAtomicExpression(NumberLiteral(1)),
                                                  NumberLiteral(0)
                                              ], [',', ';', ','])
                                          ),
                                          ReturnStatement(
                                              MultiplicativeExpression([
                                                  Identifier('matrix'),
                                                  Identifier('rot')], ['*'])
                                          )
                                      ]))
        # Starting the test.
        parser = syntactic_analyzer_pipeline(content)
        # noinspection PyUnresolvedReferences
        result = parser._SyntacticAnalyzer__try_parse_function_definition()
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
