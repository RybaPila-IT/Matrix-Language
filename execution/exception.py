class ExecutionException(Exception):
    def __init__(self):
        super().__init__()


class MissingMainException(ExecutionException):
    def __init__(self):
        super().__init__()


class WithStackTraceException(ExecutionException):
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
        self.identifier = identifier
        self.expected = expected
        self.received = received


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


class InvalidMatrixLiteralException(WithStackTraceException):
    def __init__(self):
        super().__init__()


class IndexException(WithStackTraceException):
    def __init__(self, index_error):
        super().__init__()
        self.error = index_error


class UndefinedVariableException(WithStackTraceException):
    def __init__(self):
        super().__init__()
