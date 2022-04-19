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


if __name__ == '__main__':
    unittest.main()
