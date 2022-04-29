import sys
import math
import numpy as np

from execution.variable import Variable, VariableType
from execution.exception import WithStackTraceException, FunctionArgumentsMismatchException, InvalidTypeException


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
            'full': StandardLibrary.__full
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
        except ValueError as e:
            e_print(e)
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
    def __transpose(args, interpreter):
        if (args_len := len(args)) != 1:
            raise FunctionArgumentsMismatchException('transpose', 1, args_len)
        variable = args[0]
        if variable.type != VariableType.MATRIX:
            e_print('Error: Transpose function must obtain a matrix')
            raise InvalidTypeException(variable.type)

        variable.value = variable.value.T
        interpreter.result = variable

    @staticmethod
    def __ident(args, interpreter):
        if (args_len := len(args)) != 1:
            raise FunctionArgumentsMismatchException('ident', 1, args_len)
        variable = args[0]
        if variable.type != VariableType.NUMBER:
            e_print('Error: Ident function must obtain a number')
            raise InvalidTypeException(variable.type)

        interpreter.result = Variable(VariableType.MATRIX, np.identity(variable.value))

    @staticmethod
    def __size(args, interpreter):
        if (args_len := len(args)) != 1:
            raise FunctionArgumentsMismatchException('size', 1, args_len)
        variable = args[0]
        if variable.type != VariableType.MATRIX:
            e_print('Error: Size function must obtain a matrix')
            raise InvalidTypeException(variable.type)

        interpreter.result = Variable(
            VariableType.MATRIX,
            np.array([list(variable.value.shape)])
        )

    @staticmethod
    def __full(args, interpreter):
        if (args_len := len(args)) != 3:
            raise FunctionArgumentsMismatchException('full', 3, args_len)
        rows, cols, value = args
        if rows.type != VariableType.NUMBER:
            e_print('Error: Full function must obtain a numbers only')
            raise InvalidTypeException(rows.type)
        if cols.type != VariableType.NUMBER:
            e_print('Error: Full function must obtain a numbers only')
            raise InvalidTypeException(cols.type)
        if value.type != VariableType.NUMBER:
            e_print('Error: Full function must obtain a numbers only')
            raise InvalidTypeException(value.type)

        interpreter.result = Variable(
            VariableType.MATRIX,
            np.full((rows.value, cols.value), value.value)
        )
