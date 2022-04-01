from enum import Enum, auto


class TokenType(Enum):
    # Identifier.
    IDENTIFIER = auto(),
    # Control-flow statements.
    IF = auto(),
    ELSE = auto(),
    UNTIL = auto(),
    RETURN = auto(),
    # Basic data types.
    NUMBER = auto(),
    STRING = auto(),
    # Logic operators.
    NOT = auto(),
    AND = auto(),
    OR = auto(),
    # Comparison operators.
    LESS = auto(),
    LESS_OR_EQUAL = auto(),
    GREATER = auto(),
    GREATER_OR_EQUAL = auto(),
    EQUAL = auto(),
    NOT_EQUAL = auto(),
    # Numerical operators.
    PLUS = auto(),
    MINUS = auto(),
    MULTIPLY = auto(),
    DIVIDE = auto(),
    # Parenthesis and brackets.
    OPEN_ROUND_BRACKET = auto(),
    CLOSE_ROUND_BRACKET = auto(),
    OPEN_CURLY_BRACKET = auto(),
    CLOSE_CURLY_BRACKET = auto(),
    OPEN_SQUARE_BRACKET = auto(),
    CLOSE_SQUARE_BRACKET = auto(),
    # Single symbols.
    COMMA = auto(),
    ASSIGNMENT = auto(),
    COLON = auto(),
    SEMICOLON = auto()
    # EOT.
    EOT = auto()
