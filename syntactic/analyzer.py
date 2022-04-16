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
        statement_block = self.__try_parse_statement_block()
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
        return StatementBlock(self.__current_token())

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
