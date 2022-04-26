class InterpreterException(Exception):
    def __init__(self):
        super().__init__()


class MissingMainException(InterpreterException):
    def __init__(self):
        super().__init__()


class WithStackTraceException(InterpreterException):
    def __init__(self):
        super().__init__()
        self.stack = []
