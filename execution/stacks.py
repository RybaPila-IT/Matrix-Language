from execution.variable import Variable, VariableType


class FunctionStack:
    def __init__(self):
        self.scope_stack = [ScopeStack()]

    def get_variable(self, identifier):
        return self.scope_stack[-1].get_variable(identifier)

    def set_variable(self, identifier, variable):
        self.scope_stack[-1].set_variable(identifier, variable)

    def open_context(self, init_scope=None):
        self.scope_stack.append(ScopeStack(init_scope))

    def close_context(self):
        self.scope_stack.pop()

    def open_scope(self):
        self.scope_stack[-1].open_scope()

    def close_scope(self):
        self.scope_stack[-1].close_scope()


class ScopeStack:
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
        self.stack[-1][identifier] = Variable(VariableType.UNDEFINED, None)
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
