from execution.exception import *


class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.stack = _ContextStack
        self.result = None
        self.returns = False

    def execute(self):
        self.parser.construct_program().accept(self)

    def evaluate_program(self, program):
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
            e.stack.append('evaluate function definition')
            raise e

    def evaluate_statement_block(self, statement_block):
        for statement in statement_block.statements:
            try:
                statement.accept(self)
                if self.returns:
                    return
            except WithStackTraceException as e:
                e.stack.append('evaluate statement block')
                raise e

    def evaluate_if_statement(self, if_statement):
        try:
            if_statement.condition.accept(self)
            if self.result:
                if_statement.statement_block.accept(self)
            elif if_statement.else_statement is not None:
                if_statement.else_statement.accept(self)
        except WithStackTraceException as e:
            e.stack.append('evaluate if statement')
            raise e

    def evaluate_until_statement(self, until_statement):
        try:
            until_statement.condition.accept(self)
            while self.result:
                until_statement.statement_block.accept(self)
                if self.returns:
                    return
                until_statement.condition.accept(self)
        except WithStackTraceException as e:
            e.stack.append('evaluate until statement')
            raise e

    def evaluate_return_statement(self, return_statement):
        try:
            if return_statement.expression is not None:
                return_statement.expression.accept(self)
            self.returns = True
        except WithStackTraceException as e:
            e.stack.append('evaluate return statement')
            raise e


class _ContextStack:
    def __init__(self):
        self.stack = [_ScopeStack]


class _ScopeStack:
    def __init__(self, init=None):
        self.stack = [{} if init is None else init]

    def new_scope(self):
        self.stack.append({})

    def close_scope(self):
        self.stack.pop()
