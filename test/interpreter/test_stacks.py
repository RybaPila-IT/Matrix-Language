import unittest

# noinspection PyProtectedMember
from execution.interpreter import _FunctionStack, _ScopeStack, _Variable, _VariableType


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
            {'i': _Variable(_VariableType.NUMBER, 42)}
        ]
        expected_scope_stacks = [
            [_ScopeStack(), _ScopeStack()],
            [_ScopeStack(), _ScopeStack({'i': _Variable(_VariableType.NUMBER, 42)})]
        ]

        for init, expected in zip(init_contexts, expected_scope_stacks):
            function_stack = _FunctionStack()
            function_stack.open_context(init)
            self.assertEqual(expected, function_stack.scope_stack)

    def test_close_context(self):
        """
        Tests function stack context closing.
        """
        function_stack = _FunctionStack()
        function_stack.scope_stack = [_ScopeStack(), _ScopeStack(), _ScopeStack()]
        expected = [_ScopeStack(), _ScopeStack()]
        function_stack.close_context()
        self.assertEqual(expected, function_stack.scope_stack)


if __name__ == '__main__':
    unittest.main()
