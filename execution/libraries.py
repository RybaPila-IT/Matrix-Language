import sys
import math

from execution.interpreter import Interpreter, _Variable, _VariableType
from execution.exception import ExecutionException


def e_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class StandardLibrary:
    @staticmethod
    def import_library():
        return {
            'print': StandardLibrary.__print,
            'cin': StandardLibrary.__cin,
            'transpose': StandardLibrary.__transpose,
            'ident': StandardLibrary.__ident,
            'size': StandardLibrary.__size,
            'fill': StandardLibrary.__fill
        }

    @staticmethod
    def __print(args: list, _):
        for arg in args:
            print(arg.value, end=' ')
        print('\n')

    @staticmethod
    def __cin(_, interpreter: Interpreter):
        try:
            number = float(input('Provide a number: '))
        except OverflowError:
            e_print('Error: Number overflow')
            raise ExecutionException()

        if math.isnan(number):
            e_print('Error: Number is NaN')
            raise ExecutionException()
        if math.isinf(number):
            e_print('Error: Number is Infinity')
            raise ExecutionException()

        interpreter.result = _Variable(
            _VariableType.NUMBER,
            number
        )


    @staticmethod
    def __transpose():
        pass

    @staticmethod
    def __ident():
        pass

    @staticmethod
    def __size():
        pass

    @staticmethod
    def __fill():
        pass
