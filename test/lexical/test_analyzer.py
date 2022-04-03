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

    def test_invalid_identifier_recognition(self):
        """
        Testing lexical analyzer behaviour on invalid identifiers.

        Test cases consist of:
            - Invalid character in identifier (different places).
            - Too long identifier.
        """
        contents = [
            (0, '$'),
            (1, 'al$_a'),
            (1, 'ala_$'),
            (1, 'ala_.'),
            (0, 'Lorem_ipsum_dolor_sit_amet_consectetur_adipiscing_elit_sed_do_eiusmod_tempor_incididunt_ut_labore_et_dolore_magna_aliqua_Ut_enim_ad_minim_veniam_quis_nostrud_exercitation_ullamco_laboris_nisi_ut_aliquip_ex_ea_commodo_consequat_Duis_aute_irure_dolor_in_reprehenderit_in_voluptate_velit_esse_cillum_dolore_eu_fugiat_nulla_pariatur_Excepteur_sint_occaecat_cupidatat_non_proident_sunt_in_culpa_qui_officia_deserunt_mollit_anim_idest_laborum')
        ]
        for reps, content in contents:
            source = positional_string_source_pipe(content)
            analyzer = LexicalAnalyzer(source)
            for i in range(reps):
                analyzer.next_token()
            with self.assertRaises(RuntimeError):
                analyzer.next_token()

    def test_keywords_recognition(self):
        """
        Testing keywords recognition by lexical analyzer.

        Testing keywords are:
            - Condition-flow statements: return, if, else, until.
            - Logic operators: and, or.
        """
        content = 'return if else until\nand or'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.RETURN, 'return', (1, 1)),
            Token(TokenType.IF, 'if', (1, 8)),
            Token(TokenType.ELSE, 'else', (1, 11)),
            Token(TokenType.UNTIL, 'until', (1, 16)),
            Token(TokenType.AND, 'and', (2, 1)),
            Token(TokenType.OR, 'or', (2, 5)),
            Token(TokenType.EOT, 'EOT', (2, 6))
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

        Language specific operators consist of: ':', ';', ',', '=' and '!'
        """
        content = ': ; , = !'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.COLON, ':', (1, 1)),
            Token(TokenType.SEMICOLON, ';', (1, 3)),
            Token(TokenType.COMMA, ',', (1, 5)),
            Token(TokenType.ASSIGNMENT, '=', (1, 7)),
            Token(TokenType.NOT, '!', (1, 9)),
            Token(TokenType.EOT, 'EOT', (1, 9))
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

    def test_valid_string_literals_recognition(self):
        """
        Tests string literals recognition by lexical analyzer.

        Test cases contain:
            - Plain string literal.
            - String literal with escaped quote sign.
        """
        content = '"This is my string"\n"This is my $"quoted$" string"'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.STRING, 'This is my string', (1, 1)),
            Token(TokenType.STRING, 'This is my "quoted" string', (2, 1)),
            Token(TokenType.EOT, 'EOT', (2, 30))
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_invalid_string_literals_recognition(self):
        """
        Tests invalid string literals recognition by lexical analyzer.

        Test cases contain:
            - Not closed string literal
            - Not closed string literal ending with escape character.
            - Not closed string literal ending with escaped quote sign.
            - Too long string literal.
        """
        contents = [
            '"This is not closed string',
            '"This is not closed string ending with escape $',
            '"This is not closed string ending with escaped quote $"',
            """\"
                Summary of  $"The Old Man and the Sea$”
                
                The story revolves around the central character, Santiago. 
                He has gone straight 84 days, without catching a single fish. 
                Due to this, the people have started seeing him as ‘salao’, 
                the worst of unluckiness. He is considered so unlucky that the young boy, 
                Manolin, who was his apprentice, is stopped by his parents to go for
                fishing with Santiago anymore. However, Manolin has admiration for Santiago and sees 
                him as a mentor. Therefore, Manolin visits Santiago each night at his shack. 
                They talk about American baseball, Manolin prepares food, and they 
                just enjoy each other’s company. One day, Santiago tells Manolin that the
                following day; he will go far out into the Gulf Stream to fish. 
                He is confident that the unluckiness, that has attached 
                itself to him, is going to wash away with this venture.
                
                On the start of 85th day of unluckiness, the old man does what he 
                decided to do. He goes far off into the Gulf Stream and very optimistically 
                waits for his big catch. At noon, Santiago sees that a big fish, which he identifies as
                a marlin, has taken his bait. Filled with joy, he tries to pull the marlin, 
                but instead, the marlin pulls the old man with his boat. He tries to tie the cord
                with the boat but fails. The marlin keeps on pulling the boat all through the
                day and night, for two days. In all this, trying to hold on to the fish, the old
                man gets badly injured and exhausted. Every time the marlin pulls hard, his hands end up 
                getting more wounded. However, just like the marlin, he does not give up.
                
                The old man admires the marlin for it staying true to its nature and struggling 
                for freedom. He feels like the marlin is partner in his pain, suffering, and also in his strength. 
                Finally, on the third day of old man’s struggling to keep the marlin, the fish tires 
                and gives in. It starts to circle around his skiff. Santiago, with all that he has in him, 
                pulls the fish and manages to kill it with a harpoon. He ties the fish to the side of the skiff 
                and finally, after days of unimaginable struggle, aims for home. Santiago is happy and proud 
                of himself that he has managed to catch a fish that would have a great price, and feed a lot of people.
                However, he is also concerned that his eaters will be unworthy of it because of its greatness.

                Just within some time, due to scent of marlin’s blood, sharks gather round. 
                They start to tear flesh away from marlin. Santiago manages to drive away a few but loses his 
                harpoon as a result. Then as more sharks keep coming, he makes another harpoon 
                by putting his knife into an oar. He kills several sharks and scares many away. 
                However, still filled with hunger, the sharks keep coming and stealing the flesh off of the marlin. 
                In the end, they leave nothing but the shell of marlin, which too only consisted of mainly its backbone,
                head, and tail. Santiago feels defeated at the loss of his precious opponent. He feels like his entire 
                struggle, and labour ended in vain and he lost. He tells the sharks too that they have 
                destroyed him and his dreams. He even blames himself for going too far.

                Santiago reaches the shore, crushed with the labour of past three days. 
                With very little that was left in him, he carries his stuff and struggles towards his shack. 
                He leaves the skeleton of the martin, which he had very arduously caught, behind. 
                He thinks that it is of no use to him now. Santiago makes it to his shack and just collapses 
                on his bed. He goes into a deep slumber and becomes oblivious to everything. 
                Now on the shore, where his boat is, fishermen gather round. 
                They see the skeleton of the marlin attached to it and measure it. 
                It turns out to be 18 feet (5.5 m) from nose to tail. The fish appears to be the biggest 
                that the village had ever seen. The fishermen tell Manolin to tell the old man 
                how sorry they are over their rude behaviour.

                Manolin gets teary when he sees the old man alive, but injured. 
                The old man tells Manolin that he lost again but Manolin assures him that everything was fine. 
                He brings him coffee and newspapers. They chat and agree on going fishing together again. 
                Some tourists that same day see the marlin’s skeleton and mistake it as a shark. 
                Now in the shack, the old man goes back to his sleep and dreams of lions that he had seen in 
                his youth when he was in Africa. (1)   \""""
        ]
        for content in contents:
            source = positional_string_source_pipe(content)
            analyzer = LexicalAnalyzer(source)
            with self.assertRaises(RuntimeError):
                analyzer.next_token()

    def test_valid_number_recognition(self):
        """
        Tests correct number representations recognitions.

        Test cases contain:
            - 0.
            - Regular integer.
            - 0 with decimal part.
            - Regular integer with decimal part.
        """
        content = '0\n42\n0.42\n42.42'
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.NUMBER, 0, (1, 1)),
            Token(TokenType.NUMBER, 42, (2, 1)),
            Token(TokenType.NUMBER, 0.42, (3, 1)),
            Token(TokenType.NUMBER, 42.42, (4, 1)),
            Token(TokenType.EOT, 'EOT', (4, 5)),
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_invalid_number_recognition(self):
        """
        Tests invalid number representation recognition.

        Test cases contain:
            - Invalid 0-starting number.
            - Empty decimal part (end of source and invalid character).
            - Number overflow.
            - Too long decimal part.
        """
        contents = [
            "042",
            "42.a",
            "42. ",
            "42.",
            "999999999999999999",
            "1.9999999999999999"
        ]
        for content in contents:
            source = positional_string_source_pipe(content)
            analyzer = LexicalAnalyzer(source)
            with self.assertRaises(RuntimeError):
                analyzer.next_token()

    def test_small_valid_program_1(self):
        content = """
                    # This line should be ignored
                    my_func() {
                        return 42.42
                    }
                """
        source = positional_string_source_pipe(content)
        expected_tokens = [
            Token(TokenType.IDENTIFIER, 'my_func', (3, 21)),
            Token(TokenType.OPEN_ROUND_BRACKET, '(', (3, 28)),
            Token(TokenType.CLOSE_ROUND_BRACKET, ')', (3, 29)),
            Token(TokenType.OPEN_CURLY_BRACKET, '{', (3, 31)),
            Token(TokenType.RETURN, 'return', (4, 25)),
            Token(TokenType.NUMBER, 42.42, (4, 32)),
            Token(TokenType.CLOSE_CURLY_BRACKET, '}', (5, 21)),
            Token(TokenType.EOT, 'EOT', (6, 16)),
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_small_valid_program_2(self):
        content = """
                    matrix[0, 2] = 13
                    matrix[:, 0] = [1.2; 1.3; 1.4;]
                """
        source = positional_string_source_pipe(content)
        expected_tokens = [
            # First line of the input.
            Token(TokenType.IDENTIFIER, 'matrix', (2, 21)),
            Token(TokenType.OPEN_SQUARE_BRACKET, '[', (2, 27)),
            Token(TokenType.NUMBER, 0, (2, 28)),
            Token(TokenType.COMMA, ',', (2, 29)),
            Token(TokenType.NUMBER, 2, (2, 31)),
            Token(TokenType.CLOSE_SQUARE_BRACKET, ']', (2, 32)),
            Token(TokenType.ASSIGNMENT, '=', (2, 34)),
            Token(TokenType.NUMBER, 13, (2, 36)),
            # Second line of the input.
            Token(TokenType.IDENTIFIER, 'matrix', (3, 21)),
            Token(TokenType.OPEN_SQUARE_BRACKET, '[', (3, 27)),
            Token(TokenType.COLON, ':', (3, 28)),
            Token(TokenType.COMMA, ',', (3, 29)),
            Token(TokenType.NUMBER, 0, (3, 31)),
            Token(TokenType.CLOSE_SQUARE_BRACKET, ']', (3, 32)),
            Token(TokenType.ASSIGNMENT, '=', (3, 34)),
            Token(TokenType.OPEN_SQUARE_BRACKET, '[', (3, 36)),
            Token(TokenType.NUMBER, 1.2, (3, 37)),
            Token(TokenType.SEMICOLON, ';', (3, 40)),
            Token(TokenType.NUMBER, 1.3, (3, 42)),
            Token(TokenType.SEMICOLON, ';', (3, 45)),
            Token(TokenType.NUMBER, 1.4, (3, 47)),
            Token(TokenType.SEMICOLON, ';', (3, 50)),
            Token(TokenType.CLOSE_SQUARE_BRACKET, ']', (3, 51)),
            # End of the sequence.
            Token(TokenType.EOT, 'EOT', (4, 16)),
        ]
        analyzer = LexicalAnalyzer(source)
        # Starting the test.
        for token in expected_tokens:
            recognized_token = analyzer.next_token()
            self.assertEqual(token.type, recognized_token.type)
            self.assertEqual(token.value, recognized_token.value)
            self.assertEqual(token.position, recognized_token.position)

    def test_small_valid_program_3(self):
        content = """
                    until(i <= 2 and j >= 5) {
                        i = i + 1.0
                        j = j - 2.0
                    }
                """
        source = positional_string_source_pipe(content)
        expected_tokens = [
            # 2nd line of the input.
            Token(TokenType.UNTIL, 'until', (2, 21)),
            Token(TokenType.OPEN_ROUND_BRACKET, '(', (2, 26)),
            Token(TokenType.IDENTIFIER, 'i', (2, 27)),
            Token(TokenType.LESS_OR_EQUAL, '<=', (2, 29)),
            Token(TokenType.NUMBER, 2, (2, 32)),
            Token(TokenType.AND, 'and', (2, 34)),
            Token(TokenType.IDENTIFIER, 'j', (2, 38)),
            Token(TokenType.GREATER_OR_EQUAL, '>=', (2, 40)),
            Token(TokenType.NUMBER, 5, (2, 43)),
            Token(TokenType.CLOSE_ROUND_BRACKET, ')', (2, 44)),
            Token(TokenType.OPEN_CURLY_BRACKET, '{', (2, 46)),
            # 3rd line of the input.
            Token(TokenType.IDENTIFIER, 'i', (3, 25)),
            Token(TokenType.ASSIGNMENT, '=', (3, 27)),
            Token(TokenType.IDENTIFIER, 'i', (3, 29)),
            Token(TokenType.PLUS, '+', (3, 31)),
            Token(TokenType.NUMBER, 1, (3, 33)),
            # 4th line of the input.
            Token(TokenType.IDENTIFIER, 'j', (4, 25)),
            Token(TokenType.ASSIGNMENT, '=', (4, 27)),
            Token(TokenType.IDENTIFIER, 'j', (4, 29)),
            Token(TokenType.MINUS, '-', (4, 31)),
            Token(TokenType.NUMBER, 2, (4, 33)),
            # 5th line of the input.
            Token(TokenType.CLOSE_CURLY_BRACKET, '}', (5, 21)),
            # End of the input.
            Token(TokenType.EOT, 'EOT', (6, 16)),
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
