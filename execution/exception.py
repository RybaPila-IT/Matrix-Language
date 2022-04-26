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
        self.identifier = identifier


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
        self.left = left
        self.right = right


class MatrixDimensionsMismatchException(WithStackTraceException):
    def __init__(self, left_dim, right_dim):
        super().__init__()
        self.left_dim = left_dim
        self.right_dim = right_dim


class ZeroDivisionException(WithStackTraceException):
    def __init__(self):
        super().__init__()


class InvalidTypeException(WithStackTraceException):
    def __init__(self, rec_type):
        super().__init__()
        self.type = rec_type
