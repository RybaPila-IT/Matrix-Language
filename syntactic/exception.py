from tokens.token import Token
from tokens.type import *


class FunctionDuplicationException(Exception):
    def __init__(self, identifier):
        self.identifier = identifier


class WithContextException(Exception):
    def __init__(self, context):
        super().__init__()
        self.context = context


class UnexpectedTokenException(WithContextException):
    def __init__(self, token, context):
        super().__init__(context)
        self.token = token


class MissingConditionException(WithContextException):
    def __init__(self, token, context):
        super().__init__(context)
        self.token = token


class MissingExpressionException(WithContextException):
    def __init__(self, token, context):
        super().__init__(context)
        self.token = token


class MissingStatementBlockException(WithContextException):
    def __init__(self, token, context):
        super().__init__(context)
        self.token = token


class MissingElseStatementException(WithContextException):
    def __init__(self, token, context):
        super().__init__(context)
        self.token = token


class MissingSelectorException(WithContextException):
    def __init__(self, token, context):
        super().__init__(context)
        self.token = token


class TokenMismatchException(WithContextException):
    def __init__(self, expected, received, context):
        super().__init__(context)
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

    def __init__(self, expected_bracket_type, received, context):
        expected = Token(
            token_type=expected_bracket_type,
            value=self.__bracket_lookup_table[expected_bracket_type],
            position=received.position
        )
        super().__init__(expected, received, context)


class MissingIdentifierException(TokenMismatchException):
    def __init__(self, received, context):
        expected = Token(
            token_type=TokenType.IDENTIFIER,
            value='',
            position=received.position
        )
        super().__init__(expected, received, context)
