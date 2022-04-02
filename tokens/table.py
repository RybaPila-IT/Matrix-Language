from tokens.type import TokenType


class TokenLookUpTable:
    """
    TokenLookUpTable contains dictionaries mapping code entities into TokenTypes.

    TokenLookUpTable contains dictionaries with:
         - keywords
         - comparison operators
         - parenthesis
         - numerical operators
         - assignment, colon, semicolon and coma
    """
    keywords = {
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "until": TokenType.UNTIL,
        "return": TokenType.RETURN,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT
    }
    comparison = {
        "<=": TokenType.LESS_OR_EQUAL,
        ">=": TokenType.GREATER_OR_EQUAL,
        "==": TokenType.EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
    }
    parenthesis = {
        "(": TokenType.OPEN_ROUND_BRACKET,
        ")": TokenType.CLOSE_ROUND_BRACKET,
        "{": TokenType.OPEN_CURLY_BRACKET,
        "}": TokenType.CLOSE_CURLY_BRACKET,
        "[": TokenType.OPEN_SQUARE_BRACKET,
        "]": TokenType.CLOSE_SQUARE_BRACKET
    }
    numerical = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MULTIPLY,
        "/": TokenType.DIVIDE,
    }
    special = {
        ",": TokenType.COMMA,
        ":": TokenType.COLON,
        ";": TokenType.SEMICOLON,
        ":=": TokenType.ASSIGNMENT
    }

