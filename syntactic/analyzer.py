from syntactic.context import SyntacticContext as Sc
from syntax_tree.constructions import *
from syntactic.exception import *


class SyntacticAnalyzer:
    """
    Class performing the syntactic analysis of the source code.

    Syntactic analyzer (parser) execution is the second step in
    the analysis of the obtained program source code.
    It produces the syntax tree representation of the source code.
    Note: in this implementation the resulting tree slightly differs from
    traditional programming tree, but it keeps the general conventions.

    The allowed constructions of the program are specified by the language
    grammar. For more information on grammar, see README.md.

    Syntactic analyzer works with tokens, which are provided by the lexical
    analyzer. Tokens are transformed into relevant syntactic constructions
    which may be simple (ex. NumberLiteral) or compound (MatrixLiteral).
    See README.md for more information on allowed constructions.
    """

    def __init__(self, lexer):
        """
        SyntacticAnalyzer constructor.

        :param lexer: instance of the LexicalAnalyzer class.
        """
        self.lexer = lexer
        self.token = None
        # Invariant: in token field we keep the fresh
        # token which was not seen before.
        self.__next_token()

    def construct_program(self):
        """
        Attempt to parse the provided source code.

        This method tries to construct the program out of provided
        source code, which is wrapped by the LexicalAnalyzer.

        If the SyntacticAnalyzer discovers an error in source code,
        it will throw an error without any attempt to fix the issue.

        See README.md for language grammar reference.

        :return: syntax_tree.constructions.Program class representing the parsed program.
        """
        functions_definitions = {}
        while (new_func_def := self.__try_parse_function_definition()) is not None:
            if new_func_def.identifier in functions_definitions:
                raise FunctionDuplicationException(new_func_def.identifier)
            functions_definitions[new_func_def.identifier] = new_func_def

        return Program(functions_definitions)

    def __try_parse_function_definition(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return None
        identifier = self.__current_token_value_then_next()
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            raise MissingBracketException(TokenType.OPEN_ROUND_BRACKET, self.__current_token(), Sc.FunctionDefinition)
        parameters = self.__try_parse_parameters()
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token(), Sc.FunctionDefinition)
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise MissingStatementBlockException(self.__current_token(), Sc.FunctionDefinition)

        return FunctionDefinition(identifier, parameters, statement_block)

    def __try_parse_parameters(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return []
        identifiers = [Identifier(self.__current_token_value_then_next())]
        while self.__is_token_then_next(TokenType.COMMA):
            # Since the ',' sign appeared, the identifier must follow.
            if not self.__is_token(TokenType.IDENTIFIER):
                raise MissingIdentifierException(self.__current_token(), Sc.Parameters)
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
                raise UnexpectedTokenException(self.__current_token(), Sc.StatementBlock)

            statements.append(result)

        # The '}' is already consumed by the '__is_token_then_next' method.
        return StatementBlock(statements)

    def __try_parse_if_statement(self):
        if not self.__is_token_then_next(TokenType.IF):
            return None
        condition = self.__try_parse_mandatory_parenthesised_or_condition()
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise MissingStatementBlockException(self.__current_token(), Sc.IfStatement)
        if not self.__is_token_then_next(TokenType.ELSE):
            return IfStatement(condition, statement_block)
        for try_parse in [self.__try_parse_statement_block,
                          self.__try_parse_if_statement]:
            if (else_statement := try_parse()) is not None:
                return IfStatement(condition, statement_block, else_statement)

        # After the 'else' constant the statement must follow.
        raise MissingElseStatementException(self.__current_token(), Sc.IfStatement)

    def __try_parse_until_statement(self):
        if not self.__is_token_then_next(TokenType.UNTIL):
            return None
        condition = self.__try_parse_mandatory_parenthesised_or_condition()
        if (statement_block := self.__try_parse_statement_block()) is None:
            raise MissingStatementBlockException(self.__current_token(), Sc.UntilStatement)

        return UntilStatement(condition, statement_block)

    def __try_parse_mandatory_parenthesised_or_condition(self):
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            # The or condition is mandatory, so the '(' token must be present.
            raise MissingBracketException(TokenType.OPEN_ROUND_BRACKET, self.__current_token(), Sc.OrCondition)
        if (condition := self.__try_parse_or_condition()) is None:
            raise MissingConditionException(self.__current_token(), Sc.OrCondition)
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token(), Sc.OrCondition)

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
                raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token(), Sc.FunctionCall)

            return FunctionCall(identifier, arguments)
        # Here we know, that we are parsing assignment statement.
        index_operator = self.__try_parse_index_operator()
        if not self.__is_token_then_next(TokenType.ASSIGNMENT):
            raise UnexpectedTokenException(self.__current_token(), Sc.Assignment)
        if (expression := self.__try_parse_additive_expression()) is None:
            raise MissingExpressionException(self.__current_token(), Sc.Assignment)

        return AssignStatement(Identifier(identifier, index_operator), expression)

    def __try_parse_index_operator(self):
        if not self.__is_token_then_next(TokenType.OPEN_SQUARE_BRACKET):
            return None
        if (first_selector := self.__try_parse_selector()) is None:
            raise MissingSelectorException(self.__current_token(), Sc.IndexOperator)
        if not self.__is_token_then_next(TokenType.COMMA):
            raise UnexpectedTokenException(self.__current_token(), Sc.IndexOperator)
        if (second_selector := self.__try_parse_selector()) is None:
            raise MissingSelectorException(self.__current_token(), Sc.IndexOperator)
        if not self.__is_token_then_next(TokenType.CLOSE_SQUARE_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_SQUARE_BRACKET, self.__current_token(), Sc.IndexOperator)

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
                raise MissingExpressionException(self.__current_token(), Sc.AdditiveExpression)
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
                raise MissingExpressionException(self.__current_token(), Sc.MultiplicativeExpression)
            atomic_expressions.append(atomic_expression)

        return atomic_expression if len(atomic_expressions) == 1 else \
            MultiplicativeExpression(atomic_expressions, operators)

    def __try_parse_atomic_expression(self):
        negated = self.__is_token_then_next(TokenType.MINUS)
        for try_parse in [self.__try_parse_identifier_or_function_call,
                          self.__try_parse_parenthesised_or_condition,
                          self.__try_parse_literal]:
            if (atomic_expression := try_parse()) is not None:
                return NegatedAtomicExpression(atomic_expression) if negated \
                    else atomic_expression
        # If we have read the negation sign, but were unable to parse anything,
        # it means an error.
        if negated:
            raise MissingExpressionException(self.__current_token(), Sc.AtomicExpression)

        return None

    def __try_parse_identifier_or_function_call(self):
        if not self.__is_token(TokenType.IDENTIFIER):
            return None
        identifier = self.__current_token_value_then_next()
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            return Identifier(identifier, self.__try_parse_index_operator())
        # Here we know that we are parsing function call.
        args = self.__try_parse_arguments()
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token(), Sc.FunctionCall)

        return FunctionCall(identifier, args)

    def __try_parse_arguments(self):
        if (expression := self.__try_parse_additive_expression()) is None:
            return []
        arguments = [expression]
        while self.__is_token_then_next(TokenType.COMMA):
            if (expression := self.__try_parse_additive_expression()) is None:
                raise MissingExpressionException(self.__current_token(), Sc.Arguments)
            arguments.append(expression)

        return arguments

    def __try_parse_parenthesised_or_condition(self):
        if not self.__is_token_then_next(TokenType.OPEN_ROUND_BRACKET):
            return None
        if (or_condition := self.__try_parse_or_condition()) is None:
            raise MissingConditionException(self.__current_token(), Sc.OrCondition)
        if not self.__is_token_then_next(TokenType.CLOSE_ROUND_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_ROUND_BRACKET, self.__current_token(), Sc.OrCondition)

        return or_condition

    def __try_parse_or_condition(self):
        if (and_condition := self.__try_parse_and_condition()) is None:
            return None
        and_conditions = [and_condition]
        while self.__is_token_then_next(TokenType.OR):
            if (and_condition := self.__try_parse_and_condition()) is None:
                raise MissingConditionException(self.__current_token(), Sc.OrCondition)
            and_conditions.append(and_condition)

        return and_condition if len(and_conditions) == 1 \
            else OrCondition(and_conditions)

    def __try_parse_and_condition(self):
        if (rel_condition := self.__try_parse_relation_condition()) is None:
            return None
        rel_conditions = [rel_condition]
        while self.__is_token_then_next(TokenType.AND):
            if (rel_condition := self.__try_parse_relation_condition()) is None:
                raise MissingConditionException(self.__current_token(), Sc.AndCondition)
            rel_conditions.append(rel_condition)

        return rel_condition if len(rel_conditions) == 1 \
            else AndCondition(rel_conditions)

    def __try_parse_relation_condition(self):
        negated = self.__is_token_then_next(TokenType.NOT)
        if (left_expression := self.__try_parse_additive_expression()) is None:
            if negated:
                raise MissingExpressionException(self.__current_token(), Sc.RelationCondition)
            return None
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
                    raise MissingExpressionException(self.__current_token(), Sc.RelationCondition)
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
            raise MissingExpressionException(self.__current_token(), Sc.MatrixLiteral)
        expressions = [expression]
        separators = []
        while self.__is_token(TokenType.COMMA) or self.__is_token(TokenType.SEMICOLON):
            separators.append(self.__current_token_value_then_next())
            if (expression := self.__try_parse_additive_expression()) is None:
                raise MissingExpressionException(self.__current_token(), Sc.MatrixLiteral)
            expressions.append(expression)
        if not self.__is_token_then_next(TokenType.CLOSE_SQUARE_BRACKET):
            raise MissingBracketException(TokenType.CLOSE_SQUARE_BRACKET, self.__current_token(), Sc.MatrixLiteral)

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
