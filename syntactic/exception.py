from tokens.token import Token
from tokens.type import *


class SyntacticException(Exception):
    def __init__(self):
        super().__init__()


class FunctionDuplicationException(SyntacticException):
    def __init__(self, identifier):
        super().__init__()
        self.identifier = identifier


class WithContextException(SyntacticException):
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
        self.expected = expected
        self.received = received


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
