import numpy as np
from enum import Enum, auto


class Variable:
    def __init__(self, var_type, value):
        self.type = var_type
        self.value = value

    def __eq__(self, other):
        if type(other) is type(self):
            if self.type == VariableType.MATRIX and other.type == VariableType.MATRIX:
                return np.all(self.value == other.value)
            return self.type == other.type and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.type, self.value))

    def __repr__(self):
        return f'Variable: type: {self.type}, value: {self.value}'


class VariableType(Enum):
    MATRIX = auto(),
    NUMBER = auto(),
    STRING = auto(),
    DOTS = auto(),
    UNDEFINED = auto()
