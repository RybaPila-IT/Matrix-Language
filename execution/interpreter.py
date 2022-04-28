import numpy as np
from enum import Enum, auto

from execution.exception import *


class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.program_functions = {}
        self.lib_functions = {}
        self.stack = _FunctionStack()
        self.result = None
        self.returns = False
        # Invariant: result contains recent variable result of
        # execution and returns is a flag informing about
        # return statement being executed.

        self.__load_library_functions()

    def execute(self):
        self.parser.construct_program().accept(self)

    def evaluate_program(self, program):
        # Store program functions definitions for performing function
        # calls arguments binding.
        self.__load_program_functions(program)
        # Without main there is no possibility to execute the program.
        if 'main' not in program.functions_definitions:
            raise MissingMainException()
        main = program.functions_definitions['main']
        try:
            main.accept(self)
        except WithStackTraceException as e:
            e.stack.append('evaluate program')
            raise e

    def evaluate_function_definition(self, function_def):
        try:
            function_def.statement_block.accept(self)
        except WithStackTraceException as e:
            e.stack.append(f'evaluate function {function_def.identifier}')
            raise e

    def evaluate_statement_block(self, statement_block):
        # Statement block always creates new scope of execution.
        self.stack.open_scope()
        for statement in statement_block.statements:
            try:
                statement.accept(self)
                if self.returns:
                    # Break since we have to close scope before returning.
                    break
            except WithStackTraceException as e:
                e.stack.append('evaluate statement block')
                raise e
        # Statement block ended, time to close the scope.
        self.stack.close_scope()

    def evaluate_if_statement(self, if_statement):
        try:
            self.__evaluate_condition(if_statement.condition)
            if self.result:
                if_statement.statement_block.accept(self)
            elif if_statement.else_statement is not None:
                if_statement.else_statement.accept(self)
        except WithStackTraceException as e:
            e.stack.append('evaluate if statement')
            raise e

    def evaluate_until_statement(self, until_statement):
        try:
            self.__evaluate_condition(until_statement.condition)
            while self.result:
                until_statement.statement_block.accept(self)
                if self.returns:
                    return
                self.__evaluate_condition(until_statement.condition)
        except WithStackTraceException as e:
            e.stack.append('evaluate until statement')
            raise e

    def __evaluate_condition(self, condition):
        condition.accept(self)
        # Sometimes we have co cast Identifier into bool.
        if not type(self.result) is bool:
            self.__evaluate_result_into_bool()

    def evaluate_return_statement(self, return_statement):
        try:
            if return_statement.expression is not None:
                return_statement.expression.accept(self)
            else:
                self.result = _Variable(_VariableType.UNDEFINED, None)
            self.returns = True
        except WithStackTraceException as e:
            e.stack.append('evaluate return statement')
            raise e

    def evaluate_function_call(self, function_call):
        args = self.__evaluate_function_call_arguments(function_call)
        # Functions defined in program source code behaves different than
        # those defined in libraries.
        if (identifier := function_call.identifier) in self.program_functions:
            self.__bind_and_evaluate_program_function(identifier, args)
        elif identifier in self.lib_functions:
            self.__bind_and_evaluate_library_function(identifier, args)
        else:
            # There is no other place, where the function may be present.
            raise UndefinedFunctionException(identifier)

    def __evaluate_function_call_arguments(self, function_call):
        evaluated_arguments = []
        for argument in function_call.arguments:
            try:
                argument.accept(self)
                evaluated_arguments.append(self.result)
            except WithStackTraceException as e:
                e.stack.append(f'evaluate function {function_call.identifier} arguments')
        return evaluated_arguments

    def __bind_and_evaluate_program_function(self, identifier, args):
        function_def = self.program_functions[identifier]
        if len(function_def.parameters) != len(args):
            raise FunctionArgumentsMismatchException(identifier, len(function_def.parameters), len(args))
        # Binding the arguments with names.
        initial_scope = {}
        for ident, arg in zip(function_def.parameters, args):
            initial_scope[ident.name] = arg
        # Preparing fresh context for the function call with
        # bonded arguments placed in the initial scope.
        self.stack.open_context(initial_scope)
        # Evaluate the function call as the function definition.
        function_def.accept(self)
        # Clearing the flag for returning, since we do not want to
        # end outer function execution yet and popping the context.
        self.returns = False
        self.stack.close_context()

    def __bind_and_evaluate_library_function(self, identifier, args):
        # TODO (radek.r) Implement this method.
        pass

    def evaluate_assign_statement(self, assign_statement):
        try:
            assign_statement.expression.accept(self)
            result = self.result
            variable = self.stack.get_variable(assign_statement.identifier.name)
            if assign_statement.identifier.index_operator is not None:
                self.__modify_variable_with_index_operator(variable, assign_statement.identifier.index_operator, result)
            else:
                self.__check_variables_types_matching(variable, result, for_assignment=True)
                self.stack.set_variable(assign_statement.identifier.name, result)
        except WithStackTraceException as e:
            e.stack.append('evaluate assign statement')
            raise e

    def __modify_variable_with_index_operator(self, variable, index_operator, result):
        try:
            if variable.type is not _VariableType.MATRIX:
                raise InvalidTypeException(variable.type)
            if result.type not in [_VariableType.MATRIX, _VariableType.NUMBER]:
                raise InvalidTypeException(result.type)

            first, second = self.__evaluate_selectors(index_operator)

            if first.type == _VariableType.DOTS and second.type == _VariableType.DOTS:
                variable.value[:, :] = result.value
            elif first.type == _VariableType.NUMBER and second.type == _VariableType.DOTS:
                variable.value[first.value, :] = result.value
            elif first.type == _VariableType.DOTS and second.type == _VariableType.NUMBER:
                variable.value[:, second.value] = result.value
            else:
                variable.value[first.value, second.value] = result.value

        except ValueError as e:
            raise IndexException(e)
        except WithStackTraceException as e:
            e.stack.append('modify variable by index operator')
            raise e

    def evaluate_additive_expression(self, add_expression):
        try:
            # Hacky solution: append some dummy operator at the beginning  in order to use zip function.
            # Below if ... else ... condition will always avoid this dummy operator usage.
            operators = ['_', *add_expression.operators]
            prev_result = None

            for mul_expr, operator in zip(add_expression.multiplicative_expressions, operators):
                mul_expr.accept(self)
                result = self.result
                if prev_result is None:
                    prev_result = result
                else:
                    self.__check_variables_types_matching(prev_result, result)
                    self.__combine_additive_variables(prev_result, result, operator)
                    prev_result = self.result

        except WithStackTraceException as e:
            e.stack.append('evaluate additive expression')
            raise e

    @staticmethod
    def __check_variables_types_matching(left, right, for_assignment=False):
        # Special case for the assignment statement.
        if for_assignment and left.type == _VariableType.UNDEFINED and right.type != _VariableType.UNDEFINED:
            return
        # Normally, we do not allow undefined variables to appear.
        if left.type == _VariableType.UNDEFINED or right.type == _VariableType.UNDEFINED:
            raise UndefinedVariableException()
        if left.type == right.type:
            return
        # Matrix + Number and Matrix * Number is ok for expressions,
        # but for assignment types must be the same on both sides.
        if not for_assignment and left.type == _VariableType.MATRIX and right.type == _VariableType.NUMBER:
            return
        # Any other combinations of types are forbidden.
        raise TypesMismatchException(left.type, right.type)

    def __combine_additive_variables(self, left, right, operator):
        match operator:
            case '+':
                if left.type == _VariableType.MATRIX and right.type == _VariableType.MATRIX:
                    self.result = _Variable(_VariableType.MATRIX, np.add(left.value, right.value))
                else:
                    self.result = _Variable(left.type, left.value + right.value)
            case '-':
                if left.type == _VariableType.MATRIX and right.type == _VariableType.MATRIX:
                    self.result = _Variable(_VariableType.MATRIX, np.add(left.value, np.negative(right.value)))
                else:
                    self.result = _Variable(left.type, left.value - right.value)

    def evaluate_multiplicative_expression(self, mul_expression):
        try:
            # Hacky solution: append some dummy operator at the beginning  in order to use zip function.
            # Below if ... else ... condition will always avoid this dummy operator usage.
            operators = ['_', *mul_expression.operators]
            prev_result = None

            for atomic_expression, operator in zip(mul_expression.atomic_expressions, operators):
                atomic_expression.accept(self)
                result = self.result
                if prev_result is None:
                    prev_result = result
                else:
                    self.__check_variables_types_matching(prev_result, result)
                    self.__combine_multiplicative_variables(prev_result, result, operator)
                    prev_result = self.result

        except WithStackTraceException as e:
            e.stack.append('evaluate multiplicative expression')
            raise e

    def __combine_multiplicative_variables(self, left, right, operator):
        match operator:
            case '*':
                if left.type == _VariableType.MATRIX and right.type == _VariableType.MATRIX:
                    # Matrix multiplication requires separate error handling.
                    try:
                        self.result = _Variable(_VariableType.MATRIX, np.matmul(left.value, right.value))
                    except ValueError:
                        raise MatrixDimensionsMismatchException(left.value.shape, right.value.shape)
                else:
                    self.result = _Variable(left.type, left.value * right.value)
            case '/':
                if right.type == _VariableType.MATRIX and right.type == _VariableType.MATRIX:
                    raise TypesMismatchException(left.type, right.type)
                if right.type == _VariableType.NUMBER and right.value == 0:
                    raise ZeroDivisionException()
                self.result = _Variable(left.type, left.value / right.value)

    def evaluate_negated_atomic_expression(self, expression):
        try:
            expression.atomic_expression.accept(self)
            if self.result.type == _VariableType.MATRIX:
                self.result.value = np.negative(self.result.value)
                return
            if self.result.type == _VariableType.NUMBER:
                self.result.value = - self.result.value
                return
            raise InvalidTypeException(self.result.type)
        except WithStackTraceException as e:
            e.stack.append('evaluate negated atomic expression')
            raise e

    def evaluate_or_condition(self, or_condition):
        try:
            for and_condition in or_condition.and_conditions:
                and_condition.accept(self)
                if self.result:
                    break
        except WithStackTraceException as e:
            e.stack.append('evaluate or condition')
            raise e

    def evaluate_and_condition(self, and_condition):
        try:
            for rel_condition in and_condition.rel_conditions:
                rel_condition.accept(self)
                if not self.result:
                    break
        except WithStackTraceException as e:
            e.stack.append('evaluate and condition')
            raise e

    def evaluate_relation_condition(self, rel_condition):
        try:
            rel_condition.left_expression.accept(self)
            if rel_condition.operator is None:
                self.__evaluate_result_into_bool()
            else:
                left = self.result
                rel_condition.right_expression.accept(self)
                right = self.result
                self.__evaluate_comparison_into_bool(left, right, rel_condition.operator)

        except WithStackTraceException as e:
            e.stack.append('evaluate rel condition')
            raise e
        # Handle possible relation condition negation
        self.result = not self.result if rel_condition.negated else self.result

    def __evaluate_result_into_bool(self):
        if self.result.type == _VariableType.MATRIX:
            self.result = np.any(self.result.value)
            return
        if self.result.type == _VariableType.NUMBER:
            self.result = self.result.value != 0
            return
        if self.result.type == _VariableType.STRING:
            self.result = self.result.value != ''
            return

        raise InvalidTypeException(self.result.type)

    def __evaluate_comparison_into_bool(self, left, right, operator):
        invalid_types = [_VariableType.STRING, _VariableType.UNDEFINED]
        if left.type in invalid_types or right.type in invalid_types:
            raise InvalidTypeException(self.result.type)
        if left.type != right.type:
            raise TypesMismatchException(left, right)
        if left.type == _VariableType.MATRIX:
            self.__evaluate_matrix_comparison_into_bool(left, right, operator)
        else:
            self.__evaluate_number_comparison_into_bool(left, right, operator)

    def __evaluate_matrix_comparison_into_bool(self, left, right, operator):
        match operator:
            case '<':
                self.result = np.all(np.less(left.value, right.value))
            case '>':
                self.result = np.all(np.greater(left.value, right.value))
            case '>=':
                self.result = np.all(np.greater_equal(left.value, right.value))
            case '<=':
                self.result = np.all(np.less_equal(left.value, right.value))
            case '==':
                self.result = np.array_equal(left.value, right.value)
            case '!=':
                self.result = not np.array_equal(left.value, right.value)

    def __evaluate_number_comparison_into_bool(self, left, right, operator):
        match operator:
            case '<':
                self.result = left.value < right.value
            case '>':
                self.result = left.value > right.value
            case '>=':
                self.result = left.value >= right.value
            case '<=':
                self.result = left.value <= right.value
            case '==':
                self.result = left.value == right.value
            case '!=':
                self.result = left.value != right.value

    def evaluate_matrix_literal(self, matrix_literal):
        # Hacky solution, we append fake separator in order to use zip function
        # with ease.
        separators = ['_', *matrix_literal.separators]
        values = [[]]
        try:
            for expression, separator in zip(matrix_literal.expressions, separators):
                expression.accept(self)
                if self.result.type != _VariableType.NUMBER:
                    raise InvalidTypeException(self.result.type)
                if separator == ';':
                    values.append([])
                values[-1].append(self.result.value)
            # Checking whether row lengths of the matrix match.
            all_rows_same_len = all([ele == len(values[0]) for ele in [len(i) for i in values]])
            if not all_rows_same_len:
                raise InvalidMatrixLiteralException()

        except WithStackTraceException as e:
            e.stack.append('evaluate matrix literal')
            raise e

        self.result = _Variable(
            _VariableType.MATRIX,
            np.array(values)
        )

    def evaluate_number_literal(self, number_literal):
        self.result = _Variable(
            _VariableType.NUMBER,
            number_literal.value
        )

    def evaluate_string_literal(self, string_literal):
        self.result = _Variable(
            _VariableType.STRING,
            string_literal.value
        )

    def evaluate_identifier(self, identifier):
        try:
            variable = self.stack.get_variable(identifier.name)
            if identifier.index_operator is not None:
                self.__evaluate_identifier_with_index_operator(variable, identifier.index_operator)
                return
            if variable.type == _VariableType.MATRIX:
                # Matrix is passed by reference.
                self.result = variable
                return
            # Simple types are passed by value.
            self.result = _Variable(
                variable.type,
                variable.value
            )
        except WithStackTraceException as e:
            e.stack.append('evaluate identifier')
            raise e

    def __evaluate_identifier_with_index_operator(self, variable, index_operator):
        if variable.type != _VariableType.MATRIX:
            raise InvalidTypeException(variable.type)
        try:
            first, second = self.__evaluate_selectors(index_operator)
            self.__select_matrix_variable_content(variable, first, second)
        except WithStackTraceException as e:
            e.stack.append('evaluate identifier with index operator')
            raise e
        except IndexError as e:
            raise IndexException(e)

    def __evaluate_selectors(self, index_operator):
        try:
            index_operator.first_selector.accept(self)
            first = self.result
            index_operator.second_selector.accept(self)
            second = self.result
            allowed_selector_types = [_VariableType.DOTS, _VariableType.NUMBER]
            if first.type not in allowed_selector_types:
                raise InvalidTypeException(first.type)
            if second.type not in allowed_selector_types:
                raise InvalidTypeException(second.type)
        except WithStackTraceException as e:
            e.stack.append('evaluate selectors')
            raise e

        return first, second

    def __select_matrix_variable_content(self, variable, first, second):
        if first.type == _VariableType.DOTS and second.type == _VariableType.DOTS:
            self.result = variable
        elif first.type == _VariableType.NUMBER and second.type == _VariableType.DOTS:
            self.result = _Variable(_VariableType.MATRIX, variable.value[first.value, :])
        elif first.type == _VariableType.DOTS and second.type == _VariableType.NUMBER:
            self.result = _Variable(_VariableType.MATRIX, variable.value[:, second.value])
        else:
            self.result = _Variable(_VariableType.NUMBER, variable.value[first.value, second.value])

    def evaluate_dots_select(self, _):
        self.result = _Variable(_VariableType.DOTS, None)

    def __load_library_functions(self):
        # TODO (radek.r) Implement this method.
        pass

    def __load_program_functions(self, program):
        self.program_functions = program.functions_definitions.copy()


class _FunctionStack:
    def __init__(self):
        self.scope_stack = [_ScopeStack()]

    def get_variable(self, identifier):
        return self.scope_stack[-1].get_variable(identifier)

    def set_variable(self, identifier, variable):
        self.scope_stack[-1].set_variable(identifier, variable)

    def open_context(self, init_scope=None):
        self.scope_stack.append(_ScopeStack(init_scope))

    def close_context(self):
        self.scope_stack.pop()

    def open_scope(self):
        self.scope_stack[-1].open_scope()

    def close_scope(self):
        self.scope_stack[-1].close_scope()


class _ScopeStack:
    # Scope has variables binding in form of dictionary where
    # variable name is mapped to it's value.
    def __init__(self, init=None):
        self.stack = [{} if init is None else init]

    def open_scope(self):
        self.stack.append({})

    def close_scope(self):
        self.stack.pop()

    def get_variable(self, identifier):
        for scope in reversed(self.stack):
            if identifier in scope:
                return scope[identifier]
        # If we did not find the variable it means that it has
        # been initialized in the current scope.
        self.stack[-1][identifier] = _Variable(_VariableType.UNDEFINED, None)
        return self.stack[-1][identifier]

    def set_variable(self, identifier, variable):
        for scope in reversed(self.stack):
            if identifier in scope:
                value_in_scope = scope[identifier]
                # Hacky solution, we set type and value, but not the whole
                # variable since we may want to make reference changing as
                # well is some later part of the function stack.
                value_in_scope.type = variable.type
                value_in_scope.value = variable.value
                return
        # If identifier was not found the behaviour is to set the
        # identifier in current scope.
        self.stack[-1][identifier] = variable

    def __eq__(self, other):
        if type(other) is type(self):
            return self.stack == other.stack
        return False

    def __hash__(self):
        return hash(self.stack)


class _Variable:
    def __init__(self, var_type, value):
        self.type = var_type
        self.value = value

    def __eq__(self, other):
        if type(other) is type(self):
            if self.type == _VariableType.MATRIX and other.type == _VariableType.MATRIX:
                return np.all(self.value == other.value)
            return self.type == other.type and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.type, self.value))

    def __repr__(self):
        return f'Variable: type: {self.type}, value: {self.value}'


class _VariableType(Enum):
    MATRIX = auto(),
    NUMBER = auto(),
    STRING = auto(),
    DOTS = auto,
    UNDEFINED = auto()
