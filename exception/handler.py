import sys

from syntactic.exception import *
from lexical.exception import *
from execution.exception import *


def e_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class ExceptionHandler:

    def handle_lexical_exception(self, exception):
        pass

    @staticmethod
    def handle_syntactic_exception(exception):
        if type(exception) is FunctionDuplicationException:
            e_print(f'Error: duplicated {exception.identifier} function definition')
        elif type(exception) is UnexpectedTokenException:
            e_print(f'Error: Received unexpected token {exception.token} in context {exception.context}')
        elif type(exception) is MissingConditionException:
            e_print(f'Error: Expected condition but got {exception.token} in context {exception.context}')
        elif type(exception) is MissingExpressionException:
            e_print(f'Error: Expected expression but got {exception.token} in context {exception.context}')
        elif type(exception) is MissingStatementBlockException:
            e_print(f'Error: Expected statement block but got {exception.token} in context {exception.context}')
        elif type(exception) is MissingElseStatementException:
            e_print(f'Error: Expected else statement but got {exception.token} in context {exception.context}')
        elif type(exception) is MissingSelectorException:
            e_print(f'Error: Expected selector but got {exception.token} in context {exception.context}')
        elif type(exception) is TokenMismatchException:
            e_print(
                f'Error: Token mismatch; expected {exception.expected} '
                f'but got {exception.received} in context {exception.context}'
            )
        elif type(exception) is MissingBracketException:
            e_print(
                f'Error: Expected bracket {exception.expected} but got {exception.token} in context {exception.context}'
            )
        elif type(exception) is MissingIdentifierException:
            e_print(f'Error: Expected identifier but got {exception.received} in context {exception.context}')
        elif type(exception) is WithContextException:
            e_print(f'Error: In context {exception.context}')

    @staticmethod
    def handle_execution_exception(exception):
        pass
