class WithPositionException(Exception):
    def __init__(self, position):
        super(Exception, self).__init__()
        self.pos = position

    def position(self):
        return self.pos


class LargeStringException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)


class LargeIdentifierException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)


class LargeNumberException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)


class LargeDecimalPartException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)


class InvalidTokenException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)


class InvalidNumberException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)


class InvalidStringException(WithPositionException):
    def __init__(self, position):
        super(WithPositionException, self).__init__(position)
