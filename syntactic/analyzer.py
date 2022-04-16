class SyntacticAnalyzer:

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None
        # Invariant: we keep the fresh token
        # which was not seen before.
        self.__next_token()

    def __next_token(self):
        self.token = self.lexer.next_token()
