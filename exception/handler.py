import sys

from syntactic.exception import *
from lexical.exception import *
from execution.exception import *


def e_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class ExceptionHandler:

    @staticmethod
    def handle_lexical_exception(exception, source=None):
        if type(exception) is WithPositionException:
            e_print(f'Error: Lexical exception at position {exception.pos}')
        elif type(exception) is LargeStringException:
            e_print(f'Error: Large string at position {exception.pos}')
        elif type(exception) is LargeIdentifierException:
            e_print(f'Error: Large identifier at position {exception.pos}')
        elif type(exception) is LargeNumberException:
            e_print(f'Error: Large number at position {exception.pos}')
        elif type(exception) is LargeDecimalPartException:
            e_print(f'Error: Large number decimal part at position {exception.pos}')
        elif type(exception) is InvalidTokenException:
            e_print(f'Error: Invalid token at position {exception.pos}')
        elif type(exception) is InvalidNumberException:
            e_print(f'Error: Invalid number at position {exception.pos}')
        elif type(exception) is InvalidStringException:
            e_print(f'Error: Invalid string at position {exception.pos}')
        else:
            e_print(f'Error: Lexical error appeared')
            return

        if source is not None:
            ExceptionHandler.__print_exception_line(source, exception.pos)

    @staticmethod
    def __print_exception_line(source, position):
        if type(position) is tuple:
            source.set_position(0)
            for i in range(position[0] - 1):
                source.get_line()
            e_print('▼'.rjust(position[1], ' '))
        else:
            source.set_position(position)

        e_print(source.get_line())

    @staticmethod
    def handle_syntactic_exception(exception, source=None):
        if type(exception) is FunctionDuplicationException:
            e_print(f'Error: duplicated {exception.identifier} function definition')
        elif type(exception) is UnexpectedTokenException:
            e_print(f'Error: Received unexpected token {exception.token} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.token.position)
        elif type(exception) is MissingConditionException:
            e_print(f'Error: Expected condition but got {exception.token} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.token.position)
        elif type(exception) is MissingExpressionException:
            e_print(f'Error: Expected expression but got {exception.token} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.token.position)
        elif type(exception) is MissingStatementBlockException:
            e_print(f'Error: Expected statement block but got {exception.token} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.token.position)
        elif type(exception) is MissingElseStatementException:
            e_print(f'Error: Expected else statement but got {exception.token} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.token.position)
        elif type(exception) is MissingSelectorException:
            e_print(f'Error: Expected selector but got {exception.token} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.token.position)
        elif type(exception) is TokenMismatchException:
            e_print(
                f'Error: Token mismatch; expected {exception.expected} '
                f'but got {exception.received} in context {exception.context}'
            )
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.received.position)
        elif type(exception) is MissingBracketException:
            e_print(
                f'Error: Expected bracket {exception.expected} but got {exception.received} '
                f'in context {exception.context}'
            )
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.received.position)
        elif type(exception) is MissingIdentifierException:
            e_print(f'Error: Expected identifier but got {exception.received} in context {exception.context}')
            if source is not None:
                ExceptionHandler.__print_exception_line(source, exception.received.position)
        elif type(exception) is WithContextException:
            e_print(f'Error: In context {exception.context}')
        else:
            e_print(f'Error: Syntactic exception appeared')

    @staticmethod
    def handle_execution_exception(exception):
        if type(exception) is MissingMainException:
            e_print(f'Error: Missing main function')
        elif type(exception) is WithStackTraceException:
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is UndefinedFunctionException:
            e_print(f'Error: Undefined function {exception.identifier}')
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is FunctionArgumentsMismatchException:
            e_print(
                f'Error: Function {exception.identifier} arguments mismatch; expected {exception.expected} '
                f'but got {exception.received}'
            )
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is TypesMismatchException:
            e_print(f'Error: Types mismatch; left {exception.left} right {exception.right}')
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is MatrixDimensionsMismatchException:
            e_print(
                f'Error: Matrix dimensions mismatch; left dimensions {exception.left_dim} '
                f'right dimensions {exception.right_dim}'
            )
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is ZeroDivisionException:
            e_print(f'Error: Division by zero')
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is InvalidTypeException:
            e_print(f'Error: Invalid type {exception.type}')
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is InvalidMatrixLiteralException:
            e_print(f'Error: Invalid matrix literal')
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is IndexException:
            e_print(f'Error: Index operator exception')
            e_print(exception.error)
            ExceptionHandler.__print_exception_stack(exception)
        elif type(exception) is UndefinedVariableException:
            e_print(f'Error: Usage of undefined variable')
            ExceptionHandler.__print_exception_stack(exception)
        else:
            e_print(f'Error: Execution exception appeared')

    @staticmethod
    def __print_exception_stack(exception):
        e_print('Stack trace:')
        for item in reversed(exception.stack):
            e_print(item)
