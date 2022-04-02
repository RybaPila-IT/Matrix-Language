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
    }
    extensible = {
        "<=": TokenType.LESS_OR_EQUAL,
        ">=": TokenType.GREATER_OR_EQUAL,
        "==": TokenType.EQUAL,
        "!=": TokenType.NOT_EQUAL,
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
        "=": TokenType.ASSIGNMENT,
        "!": TokenType.NOT
    }
    inextensible = {
        "(": TokenType.OPEN_ROUND_BRACKET,
        ")": TokenType.CLOSE_ROUND_BRACKET,
        "{": TokenType.OPEN_CURLY_BRACKET,
        "}": TokenType.CLOSE_CURLY_BRACKET,
        "[": TokenType.OPEN_SQUARE_BRACKET,
        "]": TokenType.CLOSE_SQUARE_BRACKET,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.MULTIPLY,
        "/": TokenType.DIVIDE,
        ",": TokenType.COMMA,
        ":": TokenType.COLON,
        ";": TokenType.SEMICOLON,
    }
