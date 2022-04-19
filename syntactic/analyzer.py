from syntax_tree.constructions import *
from syntactic.exception import *


class SyntacticAnalyzer:

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = None
        # Invariant: in token field we keep the fresh
        # token which was not seen before.
        self.__next_token()

    def construct_program(self):
        functions_definitions = {}
        while (new_func_def := self.__try_parse_function_definition()) is not None:
            functions_definitions[new_func_def.identifier] = new_func_def

        return Program(functions_definitions)

    def __try_parse_function_definition(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return None
        identifier = self.__current_token_value_then_next()
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            raise MissingBracketException(TokenType.OPEN_ROUND_BRACKET, self.__current_token())
        parameters = self.__try_parse_parameters()
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise MissingBracketException(TokenType.OPEN_CURLY_BRACKET, self.__current_token())

        return FunctionDefinition(identifier, parameters, statement_block)

    def __try_parse_parameters(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return []
        identifiers = [Identifier(self.__current_token_value_then_next())]
        while self.__is_token_then_next(TokenType.COMMA):
            # Since the ',' sign appeared, the identifier must follow.
            if not self.__is_token(TokenType.IDENTIFIER):
                raise MissingIdentifierException(self.__current_token())
            identifiers.append(Identifier(self.__current_token_value_then_next()))

        return identifiers

    def __try_parse_statement_block(self):
        if not self.__is_token_then_next(TokenType.OPEN_CURLY_BRACKET):
            return None
        statements = []
        while not self.__is_token_then_next(TokenType.CLOSE_CURLY_BRACKET):
            for try_parse in [self.__try_parse_if_statement,
                              self.__try_parse_until_statement,
                              self.__try_parse_return_statement,
                              self.__try_parse_assignment_or_function_call,
                              self.__try_parse_statement_block]:
                if (result := try_parse()) is not None:
                    break

            if result is None:
                raise UnexpectedTokenException(self.__current_token())

            statements.append(result)

        # The '}' is already consumed by the '__is_token_then_next' method.
        return StatementBlock(statements)

    def __try_parse_if_statement(self):
        if not self.__is_token_then_next(TokenType.IF):
            return None
        condition = self.__try_parse_mandatory_parenthesised_or_condition()
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token_then_next(TokenType.ELSE):
            return IfStatement(condition, statement_block)
        for try_parse in [self.__try_parse_statement_block,
                          self.__try_parse_if_statement]:
            if (else_statement := try_parse()) is not None:
                return IfStatement(condition, statement_block, else_statement)

        # After the 'else' constant the statement must follow.
        raise UnexpectedTokenException(self.__current_token())

    def __try_parse_until_statement(self):
        if not self.__is_token_then_next(TokenType.UNTIL):
            return None
        condition = self.__try_parse_mandatory_parenthesised_or_condition()
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise UnexpectedTokenException(self.__current_token())

        return UntilStatement(condition, statement_block)

    def __try_parse_mandatory_parenthesised_or_condition(self):
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            # The or condition is mandatory, so the '(' token must be present.
            raise MissingBracketException(TokenType.OPEN_ROUND_BRACKET, self.__current_token())
        if (condition := self.__try_parse_or_condition()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())

        return condition

    def __try_parse_return_statement(self):
        if not self.__is_token_then_next(TokenType.RETURN):
            return None

        return ReturnStatement(self.__try_parse_additive_expression())

    def __try_parse_assignment_or_function_call(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return None
        identifier = self.__current_token_value_then_next()
        if self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            # Here we know, that we are parsing function call.
            arguments = self.__try_parse_arguments()
            if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
                raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())

            return FunctionCall(identifier, arguments)
        # Here we know, that we are parsing assignment statement.
        index_operator = self.__try_parse_index_operator()
        if not self.__is_token_then_next(TokenType.ASSIGNMENT):
            raise UnexpectedTokenException(self.__current_token())
        if (expression := self.__try_parse_additive_expression()) is None:
            raise UnexpectedTokenException(self.__current_token())

        return AssignStatement(identifier, index_operator, expression)

    def __try_parse_index_operator(self):
        if not self.__is_token_then_next(TokenType.OPEN_SQUARE_BRACKET):
            return None
        if (first_selector := self.__try_parse_selector()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token_then_next(TokenType.COMMA):
            raise UnexpectedTokenException(self.__current_token())
        if (second_selector := self.__try_parse_selector()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token_then_next(TokenType.CLOSE_SQUARE_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_SQUARE_BRACKET, self.__current_token())

        return IndexOperator(first_selector, second_selector)

    def __try_parse_selector(self):
        if self.__is_token_then_next(TokenType.COLON):
            return DotsSelect()
        return self.__try_parse_additive_expression()

    def __try_parse_additive_expression(self):
        if (mul_expression := self.__try_parse_multiplicative_expression()) is None:
            return None
        mul_expressions = [mul_expression]
        operators = []
        while self.__is_token(TokenType.PLUS) or self.__is_token(TokenType.MINUS):
            operators.append(self.__current_token_value_then_next())
            if (mul_expression := self.__try_parse_multiplicative_expression()) is None:
                # After '+' or '-' operand there must be a multiplicative expression.
                raise UnexpectedTokenException(self.__current_token())
            mul_expressions.append(mul_expression)

        return mul_expression if len(mul_expressions) == 1 \
            else AdditiveExpression(mul_expressions, operators)

    def __try_parse_multiplicative_expression(self):
        if (atomic_expression := self.__try_parse_atomic_expression()) is None:
            return None
        atomic_expressions = [atomic_expression]
        operators = []
        while self.__is_token(TokenType.MULTIPLY) or self.__is_token(TokenType.DIVIDE):
            operators.append(self.__current_token_value_then_next())
            if (atomic_expression := self.__try_parse_atomic_expression()) is None:
                # After the '*' or '/' operand there must be an atomic expression.
                raise UnexpectedTokenException(self.__current_token())
            atomic_expressions.append(atomic_expression)

        return atomic_expression if len(atomic_expressions) == 1 else \
            MultiplicativeExpression(atomic_expressions, operators)

    def __try_parse_atomic_expression(self):
        negated = False
        if self.__is_token_then_next(TokenType.MINUS):
            negated = True

        for try_parse in [self.__try_parse_identifier_or_function_call,
                          self.__try_parse_parenthesised_or_condition,
                          self.__try_parse_literal]:
            if (atomic_expression := try_parse()) is not None:
                return NegatedAtomicExpression(atomic_expression) if negated \
                    else atomic_expression
        # If we have read the negation sign, but were unable to parse anything,
        # it means an error.
        if negated:
            raise UnexpectedTokenException(self.__current_token())

        return None

    def __try_parse_identifier_or_function_call(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return None
        identifier = self.__current_token_value_then_next()
        # Consume current identifier value and check if we have the '(' token.
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            return Identifier(identifier)
        args = self.__try_parse_arguments()
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())

        return FunctionCall(identifier, args)

    def __try_parse_arguments(self):
        if self.__is_token(TokenType.CLOSE_ROUND_BRACKET):
            return []
        if (expression := self.__try_parse_additive_expression()) is None:
            raise UnexpectedTokenException(self.__current_token())
        arguments = [expression]
        while self.__is_token_then_next(TokenType.COMMA):
            if (expression := self.__try_parse_additive_expression()) is None:
                # After the comma, there must be an expression.
                raise UnexpectedTokenException(self.__current_token())
            arguments.append(expression)

        return arguments

    def __try_parse_parenthesised_or_condition(self):
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            return None
        if (or_condition := self.__try_parse_or_condition()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())

        return or_condition

    def __try_parse_or_condition(self):
        if (and_condition := self.__try_parse_and_condition()) is None:
            return None
        and_conditions = [and_condition]
        while self.__is_token_then_next(TokenType.OR):
            if (and_condition := self.__try_parse_and_condition()) is None:
                # After the or operand, there mus be an and condition.
                raise UnexpectedTokenException(self.__current_token())
            and_conditions.append(and_condition)

        return and_condition if len(and_conditions) == 1 \
            else OrCondition(and_conditions)

    def __try_parse_and_condition(self):
        if (rel_condition := self.__try_parse_relation_condition()) is None:
            return None
        rel_conditions = [rel_condition]
        while self.__is_token_then_next(TokenType.AND):
            if (rel_condition := self.__try_parse_relation_condition()) is None:
                # After the and operand, there must be an relation condition.
                raise UnexpectedTokenException(self.__current_token())
            rel_conditions.append(rel_condition)

        return rel_condition if len(rel_conditions) == 1 \
            else AndCondition(rel_conditions)

    def __try_parse_relation_condition(self):
        negated = False
        if self.__is_token_then_next(TokenType.NOT):
            negated = True
        if (left_expression := self.__try_parse_additive_expression()) is None:
            raise UnexpectedTokenException(self.__current_token())
        possible_token_types = [
            TokenType.LESS,
            TokenType.LESS_OR_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_OR_EQUAL,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL
        ]
        for token_type in possible_token_types:
            if self.__is_token(token_type):
                operator = self.__current_token_value_then_next()
                if (right_expression := self.__try_parse_additive_expression()) is None:
                    raise UnexpectedTokenException(self.__current_token())
                return RelationCondition(negated, left_expression, operator, right_expression)

        return RelationCondition(negated, left_expression) if negated \
            else left_expression

    def __try_parse_literal(self):
        if self.__is_token(TokenType.STRING):
            literal = StringLiteral(self.__current_token_value_then_next())
        elif self.__is_token(TokenType.NUMBER):
            literal = NumberLiteral(self.__current_token_value_then_next())
        else:
            literal = self.__try_parse_matrix_literal()

        return literal

    def __try_parse_matrix_literal(self):
        if not self.__is_token_then_next(TokenType.OPEN_SQUARE_BRACKET):
            return None
        if (expression := self.__try_parse_additive_expression()) is None:
            raise UnexpectedTokenException(self.__current_token())
        expressions = [expression]
        separators = []
        while self.__is_token(TokenType.COMMA) or self.__is_token(TokenType.SEMICOLON):
            separators.append(self.__current_token_value_then_next())
            if (expression := self.__try_parse_additive_expression()) is None:
                # After the separator, there must be following expression.
                raise UnexpectedTokenException(self.__current_token())
            expressions.append(expression)
        if not self.__is_token_then_next(TokenType.CLOSE_SQUARE_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_SQUARE_BRACKET, self.__current_token())

        return MatrixLiteral(expressions, separators)

    def __current_token(self):
        return self.token

    def __next_token(self):
        self.token = self.lexer.next_token()

    def __is_token(self, expected_token_type):
        return self.token.type == expected_token_type

    def __is_token_then_next(self, expected_token_type):
        if self.token.type == expected_token_type:
            self.__next_token()
            return True
        return False

    def __current_token_value_then_next(self):
        value = self.token.value
        self.__next_token()
        return value
