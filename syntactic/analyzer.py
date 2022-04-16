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
        pass

    def __try_parse_until_statement(self):
        pass

    def __try_parse_return_statement(self):
        pass

    def __try_parse_assignment_or_function_call(self):
        pass

    def __try_parse_additive_expression(self):
        if (mul_expression := self.__try_parse_multiplicative_expression()) is None:
            return None
        mul_expressions = [mul_expression]
        operators = []
        while self.__is_token(TokenType.ADD) or self.__is_token(TokenType.MINUS):
            operators.append(self.__current_token_value())
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
                          self.__try_parse_or_condition,
                          self.__try_parse_literal]:
            if (atomic_term := try_parse()) is not None:
                return AtomicExpression(negated, atomic_term)

        raise UnexpectedTokenException(self.__current_token())

    def __try_parse_identifier_or_function_call(self):
        pass

    def __try_parse_or_condition(self):
        pass

    def __try_parse_literal(self):
        pass

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
