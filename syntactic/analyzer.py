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
        identifier = self.__current_token_value()
        if not self.__is_next_token(TokenType.OPEN_ROUND_BRACKET):
            raise MissingBracketException(TokenType.OPEN_ROUND_BRACKET, self.__current_token())
        # Consume token with opening square bracket
        # in order to maintain invariant.
        self.__next_token()
        parameters = self.__try_parse_parameters()
        if not self.__is_token(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())
        # Consume token with closing square bracket
        # in order to maintain invariant.
        self.__next_token()
        statement_block = self.__try_parse_statement_block()
        if statement_block is None:
            raise MissingBracketException(TokenType.OPEN_CURLY_BRACKET, self.__current_token())
        return FunctionDefinition(identifier, parameters, statement_block)

    def __try_parse_parameters(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return []
        identifiers = [Identifier(self.__current_token_value())]
        while self.__is_next_token(TokenType.COMMA):
            # Since the ',' sign appeared, the identifier must follow.
            if not self.__is_next_token(TokenType.IDENTIFIER):
                raise MissingIdentifierException(self.__current_token())
            identifiers.append(Identifier(self.__current_token_value()))

        return identifiers

    def __try_parse_statement_block(self):
        if not self.__is_token(TokenType.OPEN_CURLY_BRACKET):
            return None
        self.__next_token()
        statements = []
        while not self.__is_token(TokenType.CLOSE_CURLY_BRACKET):
            for try_parse in [self.__try_parse_if_statement,
                              self.__try_parse_until_statement,
                              self.__try_parse_return_statement,
                              self.__try_parse_assignment_or_function_call,
                              self.__try_parse_statement_block]:
                if (result := try_parse()) is None:
                    # Here we are sure, that some statement must be present,
                    # but in reality is not.
                    raise UnexpectedTokenException(self.__current_token())
                statements.append(result)
        # Consume closing '}' bracket token
        # in order to maintain invariant.
        self.__next_token()

        return StatementBlock(statements)

    def __try_parse_if_statement(self):
        if not self.__is_token(TokenType.IF):
            return None
        self.__next_token()
        condition = self.__try_parse_mandatory_parenthesised_or_condition()
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token(TokenType.ELSE):
            return IfStatement(condition, statement_block)
        # Consuming 'else' token.
        self.__next_token()
        for try_parse in [self.__try_parse_statement_block,
                          self.__try_parse_if_statement]:
            if (else_statement := try_parse()) is not None:
                return IfStatement(condition, statement_block, else_statement)

        # After the 'else' statement the other statement must follow.
        raise UnexpectedTokenException(self.__current_token())

    def __try_parse_until_statement(self):
        if not self.__is_token(TokenType.UNTIL):
            return None
        self.__next_token()
        condition = self.__try_parse_mandatory_parenthesised_or_condition()
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise UnexpectedTokenException(self.__current_token())

        return UntilStatement(condition, statement_block)

    def __try_parse_mandatory_parenthesised_or_condition(self):
        if not self.__is_token(TokenType.OPEN_ROUND_BRACKET):
            raise MissingBracketException(TokenType.OPEN_ROUND_BRACKET, self.__current_token())
        # Consuming the '(' token.
        self.__next_token()
        if (condition := self.__try_parse_or_condition()) is None:
            raise UnexpectedTokenException(self.__current_token())
        if self.__is_token(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())
        # Consuming the ')' token.
        self.__next_token()

        return condition

    def __try_parse_return_statement(self):
        if not self.__is_token(TokenType.RETURN):
            return None

        return ReturnStatement(self.__try_parse_additive_expression())

    def __try_parse_assignment_or_function_call(self):
        pass

    def __try_parse_additive_expression(self):
        if (mul_expression := self.__try_parse_multiplicative_expression()) is None:
            return None
        mul_expressions = [mul_expression]
        operators = []
        while self.__is_token(TokenType.ADD) or self.__is_token(TokenType.MINUS):
            operators.append(self.__current_token_value())
            self.__next_token()
            if (mul_expression := self.__try_parse_multiplicative_expression()) is None:
                # After the operand, there must be a multiplicative expression.
                raise UnexpectedTokenException(self.__current_token())
            mul_expressions.append(mul_expression)

        return AdditiveExpression(mul_expressions, operators)

    def __try_parse_multiplicative_expression(self):
        if (atomic_expression := self.__try_parse_atomic_expression()) is None:
            return None
        atomic_expressions = [atomic_expression]
        operators = []
        while self.__is_token(TokenType.MULTIPLY) or self.__is_token(TokenType.DIVIDE):
            operators.append(self.__current_token_value())
            self.__next_token()
            if (atomic_expression := self.__try_parse_atomic_expression()) is None:
                # After the operand, there mus be an atomic expression.
                raise UnexpectedTokenException(self.__current_token())
            atomic_expressions.append(atomic_expression)

        return MultiplicativeExpression(atomic_expressions, operators)

    def __try_parse_atomic_expression(self):
        negated = False
        if self.__is_token(TokenType.MINUS):
            negated = True
            self.__next_token()

        for try_parse in [self.__try_parse_identifier_or_function_call,
                          self.__try_parse_parenthesised_or_condition,
                          self.__try_parse_literal]:
            if (atomic_term := try_parse()) is not None:
                return AtomicExpression(negated, atomic_term)

        raise UnexpectedTokenException(self.__current_token())

    def __try_parse_identifier_or_function_call(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return None
        identifier = self.__current_token_value()
        # Consume current identifier value and check if we have the '(' token.
        if not self.__is_next_token(TokenType.OPEN_ROUND_BRACKET):
            return Identifier(identifier)
        # Consume the '(' token.
        self.__next_token()
        args = self.__try_parse_arguments()
        if not self.__is_token(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())
        self.__next_token()

        return FunctionCall(identifier, args)

    def __try_parse_arguments(self):
        if (expression := self.__try_parse_additive_expression()) is None:
            return []
        arguments = [expression]
        while self.__is_token(TokenType.COMMA):
            # Consuming the ',' token.
            self.__next_token()
            if (expression := self.__try_parse_additive_expression()) is None:
                # After the comma, there must be an expression.
                raise UnexpectedTokenException(self.__current_token())
            arguments.append(expression)

        return arguments

    def __try_parse_parenthesised_or_condition(self):
        if not self.__is_token(TokenType.OPEN_ROUND_BRACKET):
            return None
        self.__next_token()
        or_condition = self.__try_parse_or_condition()
        if or_condition is None:
            raise UnexpectedTokenException(self.__current_token())
        if not self.__is_token(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token())
        # Consume ')' in order to maintain invariant.
        self.__next_token()

        return or_condition

    def __try_parse_or_condition(self):
        if (and_condition := self.__try_parse_and_condition()) is None:
            return None
        and_conditions = [and_condition]
        while self.__is_token(TokenType.OR):
            self.__next_token()
            if (and_condition := self.__try_parse_and_condition()) is None:
                # After the or operand, there mus be an and condition.
                raise UnexpectedTokenException(self.__current_token())
            and_conditions.append(and_condition)

        return OrCondition(and_conditions)

    def __try_parse_and_condition(self):
        if (rel_condition := self.__try_parse_relation_condition()) is None:
            return None
        rel_conditions = [rel_condition]
        while self.__is_token(TokenType.AND):
            self.__next_token()
            if (rel_condition := self.__try_parse_relation_condition()) is None:
                # After the and operand, there mus be an relation condition.
                raise UnexpectedTokenException(self.__current_token())
            rel_conditions.append(rel_condition)

        return AndCondition(rel_conditions)

    def __try_parse_relation_condition(self):
        negated = False
        if self.__is_token(TokenType.NOT):
            negated = True
            self.__next_token()
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
                operator = self.__current_token_value()
                self.__next_token()
                if (right_expression := self.__try_parse_additive_expression()) is None:
                    raise UnexpectedTokenException(self.__current_token())
                return RelationCondition(negated, left_expression, operator, right_expression)

        return RelationCondition(negated, left_expression)

    def __try_parse_literal(self):
        if self.__is_token(TokenType.STRING):
            literal = StringLiteral(self.__current_token_value())
            self.__next_token()
        elif self.__is_token(TokenType.NUMBER):
            literal = NumberLiteral(self.__current_token_value())
            self.__next_token()
        else:
            literal = self.__try_parse_matrix_literal()

        return literal

    def __try_parse_matrix_literal(self):
        if not self.__is_token(TokenType.OPEN_SQUARE_BRACKET):
            return None
        # Consume opening '[' bracket.
        self.__next_token()
        if (expression := self.__try_parse_additive_expression()) is None:
            raise UnexpectedTokenException(self.__current_token())
        expressions = [expression]
        separators = []
        while self.__is_token(TokenType.COMMA) or self.__is_token(TokenType.SEMICOLON):
            separators.append(self.__current_token_value())
            self.__next_token()
            if (expression := self.__try_parse_additive_expression()) is None:
                # After the separator, there must be following expression.
                raise UnexpectedTokenException(self.__current_token())
            expressions.append(expression)
        if not self.__is_token(TokenType.CLOSE_SQUARE_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_SQUARE_BRACKET, self.__current_token())
        # Consume ']' in order to maintain invariant.
        self.__next_token()

        return MatrixLiteral(expressions, separators)

    def __current_token(self):
        return self.token

    def __next_token(self):
        self.token = self.lexer.next_token()

    def __is_next_token(self, expected_token_type):
        self.__next_token()
        return self.__is_token(expected_token_type)

    def __is_token(self, expected_token_type):
        return self.token.type == expected_token_type

    def __current_token_value(self):
        return self.token.value
