class Program:
    def __init__(self, functions_definitions):
        self.functions_definitions = functions_definitions

    def accept(self, visitor):
        visitor.evaluate_program(self)

    def __repr__(self):
        return str.format('Program:\nFunctions: {}\n', self.functions_definitions)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.functions_definitions == other.functions_definitions
        return False

    def __hash__(self):
        return hash(self.functions_definitions)


class FunctionDefinition:
    def __init__(self, identifier, parameters, statement_block):
        self.identifier = identifier
        self.parameters = parameters
        self.statement_block = statement_block

    def accept(self, visitor):
        visitor.evaluate_function_definition(self)

    def __repr__(self):
        return str.format(
            'Function: {}\n\tParameters: {}\n\t Statement Block: {}\n',
            self.identifier,
            self.parameters,
            self.statement_block
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.identifier == other.identifier and \
                   self.parameters == other.parameters and \
                   self.statement_block == other.statement_block
        return False

    def __hash__(self):
        return hash((self.identifier, self.parameters, self.statement_block))


class StatementBlock:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return str.format('Statement block\n\tStatements: {}\n', self.statements)

    def accept(self, visitor):
        visitor.evaluate_statement_block(self)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.statements == other.statements
        return False

    def __hash__(self):
        return hash(self.statements)


class IfStatement:
    def __init__(self, condition, statement_block, else_statement=None):
        self.condition = condition
        self.statement_block = statement_block
        self.else_statement = else_statement

    def accept(self, visitor):
        visitor.evaluate_if_statement(self)

    def __repr__(self):
        return str.format(
            'IF statement\n\tCondition: {}\n\t Statement block: {}\n\t: Else statement: {}\n',
            self.condition,
            self.statement_block,
            self.else_statement
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.condition == other.condition and \
                   self.statement_block == other.statement_block and \
                   self.else_statement == other.else_statement
        return False

    def __hash__(self):
        return hash((self.condition, self.statement_block, self.else_statement))


class UntilStatement:
    def __init__(self, condition, statement_block):
        self.condition = condition
        self.statement_block = statement_block

    def accept(self, visitor):
        visitor.evaluate_until_statement(self)

    def __repr__(self):
        return str.format(
            'Until statement\n\tCondition: {}\n\tStatement block: {}\n',
            self.condition,
            self.statement_block
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.condition == other.condition and \
                   self.statement_block == other.statement_block
        return False

    def __hash__(self):
        return hash((self.condition, self.statement_block))


class ReturnStatement:
    def __init__(self, expression=None):
        self.expression = expression

    def accept(self, visitor):
        visitor.evaluate_return_statement(self)

    def __repr__(self):
        return str.format('Return statement\n\tExpression: {}\n', self.expression)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.expression == other.expression
        return False

    def __hash__(self):
        return hash(self.expression)


class FunctionCall:
    def __init__(self, identifier, arguments):
        self.identifier = identifier
        self.arguments = arguments

    def accept(self, visitor):
        visitor.evaluate_function_call(self)

    def __repr__(self):
        return str.format(
            'Function call\n\tIdentifier: {}\n\tArguments: {}\n',
            self.identifier,
            self.arguments
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.identifier == other.identifier and \
                   self.arguments == other.arguments
        return False

    def __hash__(self):
        return hash((self.identifier, self.arguments))


class AssignStatement:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def accept(self, visitor):
        visitor.evaluate_assign_statement(self)

    def __repr__(self):
        return str.format(
            'Assign statement\n\tIdentifier: {}\n\tExpression: {}\n',
            self.identifier,
            self.expression
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.identifier == other.identifier and \
                   self.expression == other.expression
        return False

    def __hash__(self):
        return hash((self.identifier, self.expression))


class AdditiveExpression:
    def __init__(self, multiplicative_expressions, operators=None):
        self.multiplicative_expressions = multiplicative_expressions
        self.operators = operators

    def accept(self, visitor):
        visitor.evaluate_additive_expression(self)

    def __repr__(self):
        return str.format(
            'Additive Expression\n\tMultiplicative expression: {}\n\tOperators: {}\n',
            self.multiplicative_expressions,
            self.operators,
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.multiplicative_expressions == other.multiplicative_expressions and \
                   self.operators == other.operators
        return False

    def __hash__(self):
        return hash((self.multiplicative_expressions, self.operators))


class MultiplicativeExpression:
    def __init__(self, atomic_expressions, operators=None):
        self.atomic_expressions = atomic_expressions
        self.operators = operators

    def accept(self, visitor):
        visitor.evaluate_multiplicative_expression(self)

    def __repr__(self):
        return str.format(
            'Multiplicative Expression\n\tAtomic expressions: {}\n\tOperators: {}\n',
            self.atomic_expressions,
            self.operators,
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.atomic_expressions == other.atomic_expressions and \
                   self.operators == other.operators
        return False

    def __hash__(self):
        return hash((self.atomic_expressions, self.operators))


class NegatedAtomicExpression:
    def __init__(self, atomic_expression):
        self.atomic_expression = atomic_expression

    def accept(self, visitor):
        visitor.evaluate_negated_atomic_expression(self)

    def __repr__(self):
        return str.format(
            'Negated Atomic Expression\n\tAtomic expression: {}\n',
            self.atomic_expression,
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.atomic_expression == other.atomic_expression
        return False

    def __hash__(self):
        return hash(self.atomic_expression)


class OrCondition:
    def __init__(self, and_conditions):
        self.and_conditions = and_conditions

    def accept(self, visitor):
        visitor.evaluate_or_condition(self)

    def __repr__(self):
        return str.format(
            'OR Condition\n\tAND conditions: {}\n',
            self.and_conditions
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.and_conditions == other.and_conditions
        return False

    def __hash__(self):
        return hash(self.and_conditions)


class AndCondition:
    def __init__(self, rel_conditions):
        self.rel_conditions = rel_conditions

    def accept(self, visitor):
        visitor.evaluate_and_condition(self)

    def __repr__(self):
        return str.format(
            'AND Condition\n\tRelation conditions: {}\n',
            self.rel_conditions
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.rel_conditions == other.rel_conditions
        return False

    def __hash__(self):
        return hash(self.rel_conditions)


class RelationCondition:
    def __init__(self, negated, left_expression, operator=None, right_expression=None):
        self.negated = negated
        self.left_expression = left_expression
        self.operator = operator
        self.right_expression = right_expression

    def __repr__(self):
        return str.format(
            'Relation Condition\n\tNegated: {}\n\tLeft expression: {}\n\tOperator: {}\n\tRight expression: {}\n',
            self.negated,
            self.left_expression,
            self.operator,
            self.right_expression
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.negated == other.negated and \
                   self.left_expression == other.left_expression and \
                   self.operator == other.operator and \
                   self.right_expression == other.right_expression
        return False

    def __hash__(self):
        return hash((self.negated, self.left_expression, self.operator, self.right_expression))


class MatrixLiteral:
    def __init__(self, expressions, separators):
        self.expressions = expressions
        self.separators = separators

    def __repr__(self):
        return str.format(
            'Matrix Literal\n\tExpressions: {}\n\tSeparators: {}\n',
            self.expressions,
            self.separators
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.expressions == other.expressions and \
                   self.separators == other.separators
        return False

    def __hash__(self):
        return hash((self.expressions, self.separators))


class StringLiteral:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str.format('String Literal\n\tValue: {}\n', self.value)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)


class NumberLiteral:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str.format('Number Literal\n\tValue: {}\n', self.value)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)


class Identifier:
    def __init__(self, name, index_operator=None):
        self.name = name
        self.index_operator = index_operator

    def __repr__(self):
        return str.format(
            'Identifier\n\tName: {}\n\tIndex operator: {}\n',
            self.name,
            self.index_operator
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and \
                    self.index_operator == other.index_operator
        return False

    def __hash__(self):
        return hash((self.name, self.index_operator))


class IndexOperator:
    def __init__(self, first_selector, second_selector):
        self.first_selector = first_selector
        self.second_selector = second_selector

    def __repr__(self):
        return str.format(
            'Index operator\n\tFirst selector: {}\n\tSecond selector: {}\n',
            self.first_selector,
            self.second_selector
        )

    def __eq__(self, other):
        if type(other) is type(self):
            return self.first_selector == other.first_selector and \
                   self.second_selector == other.second_selector
        return False

    def __hash__(self):
        return hash((self.first_selector, self.second_selector))


class DotsSelect:
    def __int__(self):
        pass

    def __repr__(self):
        return str.format('Dots Select\n')

    def __eq__(self, other):
        return type(other) is type(self)

    def __hash__(self):
        return hash(self)
