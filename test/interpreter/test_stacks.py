import unittest

from execution.variable import Variable, VariableType
from execution.stacks import FunctionStack, ScopeStack


class TestFunctionStack(unittest.TestCase):
    def test_open_context(self):
        """
        Tests function stack context opening.

        Test cases are:
            - Empty context opening
            - Context opening with initial values
        """
        init_contexts = [
            {},
            {'i': Variable(VariableType.NUMBER, 42)}
        ]
        expected_scope_stacks = [
            [ScopeStack(), ScopeStack()],
            [ScopeStack(), ScopeStack({'i': Variable(VariableType.NUMBER, 42)})]
        ]

        for init, expected in zip(init_contexts, expected_scope_stacks):
            function_stack = FunctionStack()
            function_stack.open_context(init)
            self.assertEqual(expected, function_stack.scope_stack)

    def test_close_context(self):
        """
        Tests function stack context closing.
        """
        function_stack = FunctionStack()
        function_stack.scope_stack = [ScopeStack(), ScopeStack(), ScopeStack()]
        expected = [ScopeStack(), ScopeStack()]
        function_stack.close_context()
        self.assertEqual(expected, function_stack.scope_stack)


class TestScopeStack(unittest.TestCase):
    def test_open_scope(self):
        """
        Tests new scope opening.
        """
        scope_stack = ScopeStack()
        expected_stack = [{}, {}]
        scope_stack.open_scope()
        self.assertEqual(expected_stack, scope_stack.stack)

    def test_close_scope(self):
        """
        Tests scopes closing.
        """
        scope_stack = ScopeStack()
        scope_stack.stack = [{}, {}, {}]
        expected_stack = [{}, {}]
        scope_stack.close_scope()
        self.assertEqual(expected_stack, scope_stack.stack)

    def test_get_variable(self):
        """
        Tests variable obtaining from scope stack.

        Test cases are:
            - Variable is in the last scope
            - Variable is not in the last scope
            - Variable is not present in scopes at all
        """
        stacks = [
            [{}, {'i': Variable(VariableType.NUMBER, 42)}],
            [{'i': Variable(VariableType.NUMBER, 42)}, {}, {}],
            [{}, {}]
        ]
        expected_vars = [
            Variable(VariableType.NUMBER, 42),
            Variable(VariableType.NUMBER, 42),
            Variable(VariableType.UNDEFINED, None)
        ]
        expected_stacks = [
            [{}, {'i': Variable(VariableType.NUMBER, 42)}],
            [{'i': Variable(VariableType.NUMBER, 42)}, {}, {}],
            [{}, {'i': Variable(VariableType.UNDEFINED, None)}]
        ]
        identifier = 'i'

        for stack, expected_var, expected_stack in zip(stacks, expected_vars, expected_stacks):
            scope_stack = ScopeStack()
            scope_stack.stack = stack
            result = scope_stack.get_variable(identifier)
            self.assertEqual(expected_var, result)
            self.assertEqual(expected_stack, scope_stack.stack)

    def test_set_variable(self):
        """
        Tests variable setting by scope stack

        Test cases are:
            - Variable is present in the last scope
            - Variable is present not in the last scope
            - Variable is not present in the scope stack
        """
        stacks = [
            [{}, {'i': Variable(VariableType.NUMBER, 42)}],
            [{'i': Variable(VariableType.NUMBER, 42)}, {}, {}],
            [{}, {}]
        ]
        expected_stacks = [
            [{}, {'i': Variable(VariableType.NUMBER, 12)}],
            [{'i': Variable(VariableType.NUMBER, 12)}, {}, {}],
            [{}, {'i': Variable(VariableType.NUMBER, 12)}]
        ]
        identifier = 'i'
        variable = Variable(VariableType.NUMBER, 12)

        for stack, expected_stack in zip(stacks, expected_stacks):
            scope_stack = ScopeStack()
            scope_stack.stack = stack
            scope_stack.set_variable(identifier, variable)
            self.assertEqual(expected_stack, scope_stack.stack)


if __name__ == '__main__':
    unittest.main()
