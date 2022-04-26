from execution.exception import *


class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.stack = _ContextStack

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
        print('Statement block evaluation')


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

