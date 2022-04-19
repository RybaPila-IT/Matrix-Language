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
            - <= a
            - a == :
        """
        contents = [
            '!! a',
            '<= a',
            'a == :',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
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
            - if (1 > 2) {return false} and 12
            - a and b and
            - a and if (1 > 2) {return false} and c
        """
        contents = [
            'if (1 > 2) {return false} and 12',
            'a and b and',
            'a and if (1 > 2) {return false} and c',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
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
            - if (1 > 2) {return false} or 12
            - a or b or
            - a or if (1 > 2) {return false} or c
        """
        contents = [
            'if (1 > 2) {return false} or 12',
            'a or b or',
            'a or if (1 > 2) {return false} or c',
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
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
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
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
            - * 12
            - 12 *
            - (12 * ) / 34
            - 34 * (if (1 > 2) {return false})
        """
        contents = [
            '* 12',
            '12 *',
            '(12 * ) / 34',
            '34 * (if (1 > 2) {return false})'
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
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
            - + 12
            - 12 -
            - (12 + ) - 34
            - 34 + (if (1 > 2) {return false})
        """
        contents = [
            '+ 12',
            '12 -',
            '(12 + ) - 34',
            '34 + (if (1 > 2) {return false})'
        ]
        # Starting the test.
        for content in contents:
            parser = syntactic_analyzer_pipeline(content)
            with self.assertRaises(UnexpectedTokenException):
                # noinspection PyUnresolvedReferences
                parser._SyntacticAnalyzer__try_parse_additive_expression()


if __name__ == '__main__':
    unittest.main()
