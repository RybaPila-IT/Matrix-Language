from tokens.token import Token
from tokens.type import *


class TokenMismatchException(Exception):
    def __init__(self, expected, received):
        super(Exception, self).__init__()
        self.expected_token = expected
        self.received_token = received


class MissingBracketException(TokenMismatchException):

    __bracket_lookup_table = {
        TokenType.OPEN_ROUND_BRACKET: '(',
        TokenType.CLOSE_ROUND_BRACKET: ')',
        TokenType.OPEN_CURLY_BRACKET: '{',
        TokenType.CLOSE_CURLY_BRACKET: '}',
        TokenType.OPEN_SQUARE_BRACKET: '[',
        TokenType.CLOSE_SQUARE_BRACKET: ']',
    }

    def __init__(self, expected_bracket_type, received):
        expected = Token(
            token_type=expected_bracket_type,
            value=self.__bracket_lookup_table[expected_bracket_type],
            position=received.position
        )
        super(TokenMismatchException, self).__init__(expected, received)


class MissingIdentifierException(TokenMismatchException):
    def __init__(self, received):
        expected = Token(
            token_type=TokenType.IDENTIFIER,
            value='',
            position=received.position
        )
        super(TokenMismatchException, self).__init__(expected, received)




