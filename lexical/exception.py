class LexicalException(Exception):
    def __init__(self):
        super().__init__()


class WithPositionException(LexicalException):
    def __init__(self, position):
        super().__init__()
        self.pos = position


class LargeStringException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)


class LargeIdentifierException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)


class LargeNumberException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)


class LargeDecimalPartException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)


class InvalidTokenException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)


class InvalidNumberException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)


class InvalidStringException(WithPositionException):
    def __init__(self, position):
        super().__init__(position)
