import sys
import math

from execution.variable import Variable, VariableType
from execution.exception import WithStackTraceException


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
    def __print(args, _):
        for arg in args:
            print(arg.value, end=' ')
        print('\n')

    @staticmethod
    def __cin(_, interpreter):
        try:
            number = float(input('Provide a number: '))
        except OverflowError:
            e_print('Error: Number overflow')
            raise WithStackTraceException()

        if math.isnan(number):
            e_print('Error: Number is NaN')
            raise WithStackTraceException()
        if math.isinf(number):
            e_print('Error: Number is Infinity')
            raise WithStackTraceException()

        interpreter.result = Variable(
            VariableType.NUMBER,
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
