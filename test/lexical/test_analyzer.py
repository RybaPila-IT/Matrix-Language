import unittest
from data.source.pipeline import positional_string_source_pipe
from lexical.analyzer import LexicalAnalyzer
from tokens.token import Token, TokenType


class TestLexicalAnalyzer(unittest.TestCase):

    def test_identifier_recognition(self):
        """
        Testing identifier recognition by lexical analyzer.

        Test cases are:
           - regular identifier.
           - identifier with underscore.
           - identifier with key word as sub-string.
           - identifier with numbers.
        """
        content = 'id1 my_id \nif_else h1e2l3l4o5'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.IDENTIFIER, 'id1', (1, 1)),
            Token(TokenType.IDENTIFIER, 'my_id', (1, 5)),
            Token(TokenType.IDENTIFIER, 'if_else', (2, 1)),
            Token(TokenType.IDENTIFIER, 'h1e2l3l4o5', (2, 9)),
            Token(TokenType.EOT, 'EOT', (2, 18))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_too_long_identifier_recognition(self):
        """
        Testing whether lexical analyzer throws an error on detecting too long identifier.
        """
        content = 'Lorem_ipsum_dolor_sit_amet_consectetur_adipiscing_elit_sed_do_eiusmod_tempor_incididunt_ut_labore_et_dolore_magna_aliqua_Ut_enim_ad_minim_veniam_quis_nostrud_exercitation_ullamco_laboris_nisi_ut_aliquip_ex_ea_commodo_consequat_Duis_aute_irure_dolor_in_reprehenderit_in_voluptate_velit_esse_cillum_dolore_eu_fugiat_nulla_pariatur_Excepteur_sint_occaecat_cupidatat_non_proident_sunt_in_culpa_qui_officia_deserunt_mollit_anim_idest_laborum'
        source = positional_string_source_pipe(content)
        analyzer = LexicalAnalyzer(source)
        with self.assertRaises(RuntimeError):
            analyzer.next_token()

    def test_keywords_recognition(self):
        """
        Testing keywords recognition by lexical analyzer.

        Testing keywords are:
            - Condition-flow statements: return, if, else, until.
            - Logic operators: and, or, not.
        """
        content = 'return if else until\nand or not'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.RETURN, 'return', (1, 1)),
            Token(TokenType.IF, 'if', (1, 8)),
            Token(TokenType.ELSE, 'else', (1, 11)),
            Token(TokenType.UNTIL, 'until', (1, 16)),
            Token(TokenType.AND, 'and', (2, 1)),
            Token(TokenType.OR, 'or', (2, 5)),
            Token(TokenType.NOT, 'not', (2, 8)),
            Token(TokenType.EOT, 'EOT', (2, 10))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_brackets_recognition(self):
        """
        Tests all bracket types recognition by lexical analyzer.
        """
        content = '{ ( [\n} ) ]'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.OPEN_CURLY_BRACKET, '{', (1, 1)),
            Token(TokenType.OPEN_ROUND_BRACKET, '(', (1, 3)),
            Token(TokenType.OPEN_SQUARE_BRACKET, '[', (1, 5)),
            Token(TokenType.CLOSE_CURLY_BRACKET, '}', (2, 1)),
            Token(TokenType.CLOSE_ROUND_BRACKET, ')', (2, 3)),
            Token(TokenType.CLOSE_SQUARE_BRACKET, ']', (2, 5)),
            Token(TokenType.EOT, 'EOT', (2, 5))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_numeric_operators_recognition(self):
        """
        Tests all numeric operators.

        Operators tested are: '+', '-', '*' and '/'
        """
        content = '+ - * /'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.PLUS, '+', (1, 1)),
            Token(TokenType.MINUS, '-', (1, 3)),
            Token(TokenType.MULTIPLY, '*', (1, 5)),
            Token(TokenType.DIVIDE, '/', (1, 7)),
            Token(TokenType.EOT, 'EOT', (1, 7))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_special_signs_recognition(self):
        """
        Tests language-specific operators.

        Language specific operators consist of: ':', ';', ',' and ':='
        """
        content = ': ; , :='
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.COLON, ':', (1, 1)),
            Token(TokenType.SEMICOLON, ';', (1, 3)),
            Token(TokenType.COMMA, ',', (1, 5)),
            Token(TokenType.ASSIGNMENT, ':=', (1, 7)),
            Token(TokenType.EOT, 'EOT', (1, 8))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_comparison_operators_recognition(self):
        """
        Tests comparison operators used by numbers.
        """
        content = '< <= > >= == !='
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.LESS, '<', (1, 1)),
            Token(TokenType.LESS_OR_EQUAL, '<=', (1, 3)),
            Token(TokenType.GREATER, '>', (1, 6)),
            Token(TokenType.GREATER_OR_EQUAL, '>=', (1, 8)),
            Token(TokenType.EQUAL, '==', (1, 11)),
            Token(TokenType.NOT_EQUAL, '!=', (1, 14)),
            Token(TokenType.EOT, 'EOT', (1, 15))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)


if __name__ == '__main__':
    unittest.main()
