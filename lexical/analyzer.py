from tokens.token import Token
from tokens.type import TokenType
from tokens.table import TokenLookUpTable
from lexical.exception import *


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

    default_options = {
        'MAX_STRING_SIZE': 1024,
        'MAX_IDENTIFIER_LENGTH': 256,
        'MAX_NUMBER_VALUE': 2147483647,
        'MAX_DECIMAL_PRECISION': 8
    }

    def __init__(self, positional_source, options=None):
        """
        LexicalAnalyzer constructor.

        LexicalAnalyzer requires source to be a positional source, or at least
        to implement next_char() and position() methods.

        Optional parameter 'options' should be a dictionary containing keys:
                - MAX_STRING_SIZE.
                - MAX_IDENTIFIER_LENGTH.
                - MAX_NUMBER_VALUE.
                - MAX_DECIMAL_PRECISION.

        :param positional_source: source implementing PositionalSource "interface".
        """
        self.source = positional_source
        self.buffer = ''
        self.token = None
        self.options = ({**LexicalAnalyzer.default_options, **options}
                        if options is not None
                        else LexicalAnalyzer.default_options)
        # Invariant: in buffer there is a fresh, new
        # character which needs investigation.
        self.__next_char()

    def next_token(self):
        """
        Returns next token read from the text.

        If error is encountered, RuntimeError with debug information is raised.
        Error includes:
            - Invalid identifier or character.
            - Wrong string literal.
            - Wrong number definition.
        :return: new token fetched from text.
        """
        self.__trim_input()

        if self.__end_of_text():
            return Token(
                token_type=TokenType.EOT,
                value=TokenType.EOT.name,
                position=self.__position()
            )

        for try_build in [self.__try_build_extensible_token,
                          self.__try_build_inextensible_token,
                          self.__try_build_number,
                          self.__try_build_string,
                          self.__try_build_identifier]:
            if try_build():
                return self.token

        raise InvalidTokenException(self.__position())

    def __try_build_identifier(self):
        if not self.__current_char().isalpha():
            return False

        position = self.__position()
        identifier = self.__read_identifier()
        token_type = (TokenLookUpTable.keywords[identifier]
                      if identifier in TokenLookUpTable.keywords
                      else TokenType.IDENTIFIER)
        self.token = Token(
            token_type=token_type,
            value=identifier,
            position=position
        )

        return True

    def __read_identifier(self):
        position = self.__position()
        identifier_chars = []

        while self.__current_char().isalnum() or self.__current_char() == '_':
            identifier_chars.append(self.__current_char())
            if len(identifier_chars) == self.options['MAX_IDENTIFIER_LENGTH']:
                raise LargeIdentifierException(position)
            self.__next_char()

        return ''.join(identifier_chars)

    def __try_build_inextensible_token(self):
        if (found_token_type := TokenLookUpTable.inextensible.get(self.__current_char())) is None:
            return False
        self.token = Token(
            token_type=found_token_type,
            value=self.__current_char(),
            position=self.__position()
        )
        self.__next_char()
        return True

    def __try_build_extensible_token(self):
        if (primary_token_type := TokenLookUpTable.extensible.get(self.__current_char())) is None:
            return False
        position = self.__position()
        prev_char = self.__current_char()
        self.__next_char()
        if self.__current_char() == '=':
            token_value = prev_char + self.__current_char()
            self.token = Token(
                token_type=TokenLookUpTable.extensible[token_value],
                value=token_value,
                position=position
            )
            self.__next_char()
        else:
            self.token = Token(
                token_type=primary_token_type,
                value=prev_char,
                position=position
            )
        return True

    def __try_build_number(self):
        if not self.__current_char().isdecimal():
            return False
        if self.__current_char() == '0':
            return self.__try_build_zero_starting_number()

        return self.__try_build_regular_number()

    def __try_build_zero_starting_number(self):
        number = 0
        position = self.__position()
        self.__next_char()
        if self.__current_char().isdecimal():
            raise InvalidNumberException(position)
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
        while self.__current_char().isdecimal():
            value = value * 10 + int(self.__current_char())
            if value >= self.options['MAX_NUMBER_VALUE']:
                raise LargeNumberException(position)
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
        while self.__current_char().isdecimal():
            decimal += 1
            value = value * 10 + int(self.__current_char())

            if decimal > self.options['MAX_DECIMAL_PRECISION']:
                raise LargeDecimalPartException(position)

            self.__next_char()

        if decimal == 0:
            raise InvalidNumberException(position)

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
            if self.__current_char() == '$':
                # Skip '$' sign and read next char, which
                # will be appended directly to string characters.
                self.__next_char()
            # We have reached the end of source without second quote sign.
            if self.__current_char() == '':
                raise InvalidStringException(position)

            string_chars.append(self.__current_char())

            if len(string_chars) > self.options['MAX_STRING_SIZE']:
                raise LargeStringException(position)

            self.__next_char()
        # Reading next char in order to maintain analyzer invariant.
        self.__next_char()
        return ''.join(string_chars)

    def __trim_input(self):
        while self.__current_char().isspace() or self.__current_char() == '#':
            if self.__current_char() == '#':
                self.__trim_comment()
            else:
                self.__next_char()

    def __trim_comment(self):
        while self.__current_char() != '\n' and self.__current_char() != '':
            self.__next_char()

    def __end_of_text(self):
        return self.__current_char() == ''

    def __position(self):
        row, col = self.source.position()
        return row, col - 1

    def __next_char(self):
        self.buffer = self.source.next_char()

    def __current_char(self):
        return self.buffer
