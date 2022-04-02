from tokens.type import TokenType


class Token:
    """
    Token class represents token object, which should be produced by lexical analyzer.

    Tokens contain necessary information, which enables easy identification
    (look: TokenType).
    Token values are set by the analyzer during lexical analysis phase of the
    program. Values are optional.
    Tokens contain field representing it's position in text. This field is optional.
    """
    def __init__(self, token_type: TokenType, value: '', position: (1, 1)):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self):
        return str.format('Token: type={}, value={}, position={}', self.type.name, self.value, self.position)
