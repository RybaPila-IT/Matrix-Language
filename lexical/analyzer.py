from tokens.token import Token
from tokens.type import TokenType
from tokens.table import TokenLookUpTable


class LexicalAnalyzer:
    """
    Class performing lexical analysis of the source code.

    As the result, it produces the string of tokens, which
    can be used for further program execution.
    New tokens are fetched by repeated calling the next_token()
    method.
    When the source is empty, analyzer will continue to produce
    EOT token.
    """

    MAX_STRING_SIZE = 1024
    MAX_IDENTIFIER_LENGTH = 256
    MAX_NUMBER_VALUE = 2147483647
    MAX_DECIMAL_PRECISION = 8

    def __init__(self, positional_source):
        """
        LexicalAnalyzer constructor.

        LexicalAnalyzer requires source to be a positional source, or at least
        to implement next_char() and position() methods.

        :param positional_source: source implementing PositionalSource "interface".
        """
        self.source = positional_source
        self.buffer = ''
        self.token = None
        self.finished = False
        # Invariant: in buffer there is a fresh, new
        # character which needs investigation.
        self.__next_char()

    def next_token(self):

        self.__trim_input()

        if self.finished:
            return self.token

        for try_build in [self.__try_build_symbolic_token,
                          self.__try_build_number,
                          self.__try_build_string,
                          self.__try_build_identifier]:
            if try_build():
                return self.token

        raise RuntimeError('invalid identifier at position {}'.format(self.__position()))

    def __try_build_identifier(self):
        if not self.__current_char().isalpha():
            return False

        position = self.__position()
        identifier = self.__read_identifier()
        keyword_token = self.__try_construct_keyword_token(identifier, position)

        if keyword_token is not None:
            self.token = keyword_token
        else:
            self.token = Token(
                token_type=TokenType.IDENTIFIER,
                value=identifier,
                position=position
            )

        return True

    def __read_identifier(self):
        position = self.__position()
        identifier_chars = []

        while self.__current_char().isalnum() or self.__current_char() == '_':
            identifier_chars.append(self.__current_char())
            if len(identifier_chars) == LexicalAnalyzer.MAX_IDENTIFIER_LENGTH:
                raise RuntimeError('identifier starting at position {} is too long'.format(position))
            self.__next_char()

        return ''.join(identifier_chars)

    @staticmethod
    def __try_construct_keyword_token(identifier, position):
        if identifier in TokenLookUpTable.keywords:
            return Token(
                token_type=TokenLookUpTable.keywords[identifier],
                value=identifier,
                position=position
            )
        if identifier in TokenLookUpTable.logic:
            return Token(
                token_type=TokenLookUpTable.logic[identifier],
                value=identifier,
                position=position
            )
        return None

    def __try_build_symbolic_token(self):
        if self.__current_char() in TokenLookUpTable.parenthesis:
            return self.__construct_parenthesis()
        if self.__current_char() in TokenLookUpTable.numerical:
            return self.__construct_numerical()
        elif self.__current_char() in TokenLookUpTable.special:
            return self.__construct_special()
        elif (self.__current_char() in TokenLookUpTable.comparison or
              self.__current_char() == '!' or
              self.__current_char() == '='):
            return self.__construct_comparison()

        return False

    def __construct_parenthesis(self):
        self.token = Token(
            token_type=TokenLookUpTable.parenthesis[self.__current_char()],
            value=self.__current_char(),
            position=self.__position()
        )
        # Reading next char in order to maintain analyzer invariant.
        self.__next_char()
        return True

    def __construct_numerical(self):
        self.token = Token(
            token_type=TokenLookUpTable.numerical[self.__current_char()],
            value=self.__current_char(),
            position=self.__position()
        )
        # Reading next char in order to maintain analyzer invariant.
        self.__next_char()
        return True

    def __construct_special(self):

        position = self.__position()

        if self.__current_char() == ':':
            self.__next_char()
            if self.__current_char() == '=':
                self.token = Token(
                    token_type=TokenType.ASSIGNMENT,
                    value=':=',
                    position=position
                )
            else:
                self.token = Token(
                    token_type=TokenType.COLON,
                    value=':',
                    position=position
                )
        else:
            self.token = Token(
                token_type=TokenLookUpTable.special[self.__current_char()],
                value=self.__current_char(),
                position=position
            )
        # Reading next char in order to maintain analyzer invariant.
        self.__next_char()
        return True

    def __construct_comparison(self):
        if self.__current_char() == '<' or self.__current_char() == '>':
            return self.__handle_inequality()
        if self.__current_char() == '!' or self.__current_char() == '=':
            return self.__handle_equality()

        return False

    def __handle_inequality(self):
        position = self.__position()
        start_char = self.__current_char()
        self.__next_char()
        if self.__current_char() != '=':
            self.token = Token(
                token_type=TokenLookUpTable.comparison[start_char],
                value=start_char,
                position=position
            )
        else:
            token_value = start_char + self.__current_char()
            self.token = Token(
                token_type=TokenLookUpTable.comparison[token_value],
                value=token_value,
                position=position
            )
            # Reading next char in order to maintain analyzer invariant.
            self.__next_char()

        return True

    def __handle_equality(self):
        position = self.__position()
        start_char = self.__current_char()
        self.__next_char()
        if self.__current_char() != '=':
            return False
        token_value = start_char + self.__current_char()
        self.token = Token(
            token_type=TokenLookUpTable.comparison[token_value],
            value=token_value,
            position=position
        )
        # Reading next char in order to maintain analyzer invariant.
        self.__next_char()
        return True

    def __try_build_number(self):
        if not self.__current_char().isnumeric():
            return False
        if self.__current_char() == '0':
            return self.__try_build_zero_starting_number()

        return self.__try_build_regular_number()

    def __try_build_zero_starting_number(self):
        number = 0
        position = self.__position()
        self.__next_char()
        if self.__current_char().isnumeric():
            raise RuntimeError('invalid zero-staring number at position {}'.format(position))
        if self.__current_char() == '.':
            number = self.__try_build_decimal_part()
        self.token = Token(
            token_type=TokenType.NUMBER,
            value=number,
            position=position
        )
        return True

    def __try_build_regular_number(self):
        position = self.__position()
        value = 0
        while self.__current_char().isnumeric():
            value = value * 10 + int(self.__current_char())
            if value >= LexicalAnalyzer.MAX_NUMBER_VALUE:
                raise RuntimeError('overflow of the number starting at position {}'.format(position))
            self.__next_char()
        if self.__current_char() == '.':
            value += self.__try_build_decimal_part()
        self.token = Token(
            token_type=TokenType.NUMBER,
            value=value,
            position=position
        )
        return True

    def __try_build_decimal_part(self):
        position = self.__position()
        value = 0
        decimal = 0
        # Omit '.' sign.
        self.__next_char()
        while self.__current_char().isnumeric():
            decimal += 1
            value = value * 10 + int(self.__current_char())

            if decimal > LexicalAnalyzer.MAX_DECIMAL_PRECISION:
                raise RuntimeError('too long decimal part starting at position {}'.format(position))

            self.__next_char()

        if decimal == 0:
            raise RuntimeError('invalid decimal part starting at position {}'.format(position))

        return value / (10 ** decimal)

    def __try_build_string(self):
        if self.__current_char() != '"':
            return False
        position = self.__position()
        string = self.__try_read_string_content()
        self.token = Token(
            token_type=TokenType.STRING,
            value=string,
            position=position
        )
        return True

    def __try_read_string_content(self):
        # Omit starting quote sign.
        position = self.__position()
        string_chars = []
        self.__next_char()

        while self.__current_char() != '"':
            # We have reached the end of source without second quote sign.
            if self.__current_char() == '':
                raise RuntimeError('invalid string (lack of ending) at position {}'.format(position))
            if self.__current_char() == '$':
                # Skip '$' sign and read next char, which
                # will be appended directly to string characters.
                self.__next_char()

            string_chars.append(self.__current_char())

            if len(string_chars) > LexicalAnalyzer.MAX_STRING_SIZE:
                raise RuntimeError('string starting at position {} is too long.'.format(position))

            self.__next_char()
        # Reading next char in order to maintain analyzer invariant.
        self.__next_char()
        return ''.join(string_chars)

    def __trim_input(self):
        if self.finished:
            return

        while self.__current_char().isspace() or self.__current_char() == '#':
            if self.__current_char() == '#':
                self.__trim_comment()
            else:
                self.__next_char()

        self.__check_if_finished()

    def __trim_comment(self):
        while self.__current_char() != '\n' or self.__current_char() != '':
            self.__next_char()

    def __check_if_finished(self):
        if self.__current_char() == '':
            self.finished = True
            self.token = Token(
                token_type=TokenType.EOT,
                value=TokenType.EOT.name,
                position=self.__position()
            )

    def __position(self):
        row, col = self.source.position()
        return row, col - 1

    def __next_char(self):
        self.buffer = self.source.next_char()

    def __current_char(self):
        return self.buffer