class Program:
    def __init__(self, functions_definitions):
        self.functions_definitions = functions_definitions

    def __repr__(self):
        return str.format('Program:\nFunctions: {}\n', self.functions_definitions)


class FunctionDefinition:
    def __init__(self, identifier, parameters, statement_block):
        self.identifier = identifier
        self.parameters = parameters
        self.statement_block = statement_block

    def __repr__(self):
        return str.format(
            'Function: {}\n\tParameters: {}\n\t Statement Block: {}\n',
            self.identifier,
            self.parameters,
            self.statement_block
        )


class StatementBlock:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return str.format('Statement block\n\tStatements: {}\n', self.statements)


class IfStatement:
    def __init__(self, condition, statement_block, else_statement_block=None):
        self.condition = condition
        self.statement_block = statement_block
        self.else_statement_block = else_statement_block

    def __repr__(self):
        return str.format(
            'IF statement\n\tCondition: {}\n\t Statement block: {}\n\t: Else statement block: {}\n',
            self.condition,
            self.statement_block,
            self.else_statement_block
        )


class UntilStatement:
    def __init__(self, condition, statement_block):
        self.condition = condition
        self.statement_block = statement_block

    def __repr__(self):
        return str.format(
            'Until statement\n\tCondition: {}\n\tStatement block: {}\n',
            self.condition,
            self.statement_block
        )


class ReturnStatement:
    def __init__(self, expression=None):
        self.expression = expression

    def __repr__(self):
        str.format('Return statement\n\tExpression: {}\n', self.expression)


class FunctionCall:
    def __init__(self, identifier, arguments):
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self):
        return str.format(
            'Function call\n\tIdentifier: {}\n\tArguments: {}\n',
            self.identifier,
            self.arguments
        )


class AssignStatement:
    def __init__(self, identifier, expression, index_operator=None):
        self.identifier = identifier
        self.index_operator = index_operator
        self.expression = expression

    def __repr__(self):
        return str.format(
            'Assign statement\n\tIdentifier: {}\n\tIndex operator: {}\n\tExpression: {}\n',
            self.identifier,
            self.index_operator,
            self.expression
        )


class IndexOperator:
    def __init__(self, first_expression=None, second_expression=None):
        # If expression is None, it means that ':' was used.
        self.first_expression = first_expression
        self.second_expression = second_expression

    def __repr__(self):
        return str.format(
            'Index operator\n\tFirst expression: {}\n\tSecond expression: {}\n',
            self.first_expression,
            self.second_expression
        )


class AdditiveExpression:
    def __init__(self, multiplicative_expressions, operators=None):
        self.multiplicative_expressions = multiplicative_expressions
        self.operators = operators

    def __repr__(self):
        return str.format(
            'Additive Expression\n\tMultiplicative expression: {}\n\tOperators: {}\n',
            self.multiplicative_expressions,
            self.operators,
        )


class MultiplicativeExpression:
    def __init__(self, atomic_expressions, operators=None):
        self.atomic_expressions = atomic_expressions
        self.operators = operators

    def __repr__(self):
        return str.format(
            'Multiplicative Expression\n\tAtomic expressions: {}\n\tOperators: {}\n',
            self.atomic_expressions,
            self.operators,
        )


class AtomicExpression:
    def __init__(self, negated, atomic_term):
        self.atomic_term = atomic_term
        self.negated = negated

    def __repr__(self):
        return str.format(
            'Atomic Expression\n\tAtomic term: {}\n\tNegated: {}\n',
            self.atomic_term,
            self.negated
        )


class OrCondition:
    def __init__(self, and_conditions):
        self.and_conditions = and_conditions

    def __repr__(self):
        return str.format(
            'OR Condition\n\tAND conditions: {}\n',
            self.and_conditions
        )


class AndCondition:
    def __init__(self, rel_conditions):
        self.rel_conditions = rel_conditions

    def __repr__(self):
        return str.format(
            'AND Condition\n\tRelation conditions: {}\n',
            self.rel_conditions
        )


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


class MatrixLiteral:
    def __init__(self, expression_rows):
        # Expression rows is dictionary mapping:
        # Row number --> expressions in this row.
        self.expression_rows = expression_rows

    def __repr__(self):
        return str.format('Matrix Literal\n\tExpression rows: {}', self.expression_rows)


class StringLiteral:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str.format('String Literal\n\tValue: {}\n', self.value)


class NumberLiteral:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str.format('Number Literal\n\tValue: {}\n', self.value)


class Identifier:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str.format('Identifier\n\tValue: {}\n', self.value)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)
