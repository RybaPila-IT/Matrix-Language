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


class UndefinedFunctionException(WithStackTraceException):
    def __init__(self, identifier):
        super().__init__()
        self.stack.insert(0, identifier)


class FunctionArgumentsMismatchException(WithStackTraceException):
    def __init__(self, identifier, expected, received):
        super().__init__()
        self.stack.insert(0, (identifier, expected, received))


class StringUsageException(WithStackTraceException):
    def __init__(self):
        super().__init__()


class TypesMismatchException(WithStackTraceException):
    def __init__(self, left, right):
        super().__init__()
        self.stack.insert(0, (left, right))
