# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from enum import IntEnum
from typing import Callable, Dict, List, Optional, TypeAlias

from .ast import *
from .lexer import Lexer
from .token import Token, TokenType


class OperatorPrecedence(IntEnum):
    LOWEST = 0
    EQUALS = 1          # ==
    LESSGREATER = 2     # > or <
    SUM = 3             # +
    PRODUCT = 4         # *
    PREFIX = 5          # -X or !X
    CALL = 6            # myFunction(X)
    INDEX = 7           # [


TOKEN_PRECEDENCES = {
    TokenType.EQ:       OperatorPrecedence.EQUALS,
    TokenType.NOT_EQ:   OperatorPrecedence.EQUALS,
    TokenType.LT:       OperatorPrecedence.LESSGREATER,
    TokenType.GT:       OperatorPrecedence.LESSGREATER,
    TokenType.PLUS:     OperatorPrecedence.SUM,
    TokenType.MINUS:    OperatorPrecedence.SUM,
    TokenType.SLASH:    OperatorPrecedence.PRODUCT,
    TokenType.ASTERISK: OperatorPrecedence.PRODUCT,
    TokenType.LPAREN:   OperatorPrecedence.CALL,
    TokenType.LBRACKET: OperatorPrecedence.INDEX,
}


PrefixParseFn: TypeAlias = Callable[[], Expression]
InfixParseFn: TypeAlias = Callable[[Expression], Expression]


class Parser:
    lexer: Lexer
    current_token: Token
    peek_token: Token
    errors: List[str]

    prefix_parse_fns: Dict[TokenType, PrefixParseFn]
    infix_parse_fns: Dict[TokenType, InfixParseFn]

    def __init__(self, lexer):
        self.lexer = lexer

        self.current_token = None
        self.peek_token = None

        self.errors = []

        self.prefix_parse_fns = {
            TokenType.IDENT: self.parse_identifier,
            TokenType.INT: self.parse_integer_literal,
            TokenType.STRING: self.parse_string_literal,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.BANG: self.parse_prefix_expression,
            TokenType.TRUE: self.parse_boolean_literal,
            TokenType.FALSE: self.parse_boolean_literal,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.IF: self.parse_if_expression,
            TokenType.FUNCTION: self.parse_function_literal,
            TokenType.LBRACKET: self.parse_array_literal,
            TokenType.LBRACE: self.parse_hash_literal,
        }

        self.infix_parse_fns = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.LPAREN: self.parse_call_expression,
            TokenType.LBRACKET: self.parse_index_expression,
        }

        self.next_token()
        self.next_token()

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_peek(self, token_type: TokenType) -> bool:
        if self.peek_token.type == token_type:
            self.next_token()
            return True
        self.peek_error(token_type)
        return False

    def peek_error(self, token_type: TokenType):
        self.errors.append(f"expected next token to be {token_type}, got {self.peek_token.type} instead")

    def peek_precedence(self) -> OperatorPrecedence:
        return TOKEN_PRECEDENCES.get(self.peek_token.type, OperatorPrecedence.LOWEST)

    def current_precedence(self) -> OperatorPrecedence:
        return TOKEN_PRECEDENCES.get(self.current_token.type, OperatorPrecedence.LOWEST)

    def parse_program(self) -> Program:
        program = Program()
        while self.current_token.type != TokenType.EOF:
            if statement := self.parse_statement():
                program.statements.append(statement)
            self.next_token()
        return program

    def parse_statement(self) -> Optional[Statement]:
        match self.current_token.type:
            case TokenType.LET:
                return self.parse_let_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
        return self.parse_expression_statement()

    def parse_block_statement(self) -> BlockStatement:
        block_statement = BlockStatement([])
        self.next_token()
        while not self.current_token.type == TokenType.RBRACE and not self.current_token.type == TokenType.EOF:
            if statement := self.parse_statement():
                block_statement.statements.append(statement)
            self.next_token()
        return block_statement

    def parse_let_statement(self) -> Optional[LetStatement]:
        if self.expect_peek(TokenType.IDENT):
            identifier = Identifier(self.current_token.literal)
            if self.expect_peek(TokenType.ASSIGN):
                self.next_token()
                if expression := self.parse_expression_statement():
                    return LetStatement(identifier, expression)

    def parse_return_statement(self) -> Optional[ReturnStatement]:
        self.next_token()
        if expression := self.parse_expression_statement():
            return ReturnStatement(expression)

    def parse_if_expression(self) -> Optional[IfExpression]:
        if self.expect_peek(TokenType.LPAREN):
            self.next_token()
            condition = self.parse_expression(OperatorPrecedence.LOWEST)
            if self.expect_peek(TokenType.RPAREN):
                if self.expect_peek(TokenType.LBRACE):
                    consequence = self.parse_block_statement()
                    if self.peek_token.type == TokenType.ELSE:
                        self.next_token()
                        if not self.expect_peek(TokenType.LBRACE):
                            return None
                        alternative = self.parse_block_statement()
                        return IfExpression(condition, consequence, alternative)
                    return IfExpression(condition, consequence, None)

    def parse_function_parameters(self) -> List[Identifier]:
        parameters: List[Identifier] = []
        if self.peek_token.type == TokenType.RPAREN:
            self.next_token()
            return parameters
        self.next_token()

        parameters.append(Identifier(self.current_token.literal))

        while self.peek_token.type == TokenType.COMMA:
            self.next_token()
            self.next_token()
            parameters.append(Identifier(self.current_token.literal))

        if self.expect_peek(TokenType.RPAREN):
            return parameters

    def parse_expression_list(self, end_token: TokenType) -> List[Expression]:
        expressions: List[Expression] = []
        if self.peek_token.type == end_token:
            self.next_token()
            return expressions

        self.next_token()
        expressions.append(self.parse_expression(OperatorPrecedence.LOWEST))

        while self.peek_token.type == TokenType.COMMA:
            self.next_token()
            self.next_token()
            expressions.append(self.parse_expression(OperatorPrecedence.LOWEST))

        if self.expect_peek(end_token):
            return expressions

    def parse_function_literal(self) -> FunctionLiteral:
        if self.expect_peek(TokenType.LPAREN):
            parameters = self.parse_function_parameters()
            if self.expect_peek(TokenType.LBRACE):
                body = self.parse_block_statement()
                return FunctionLiteral(parameters, body)

    def parse_array_literal(self) -> ArrayLiteral:
        return ArrayLiteral(self.parse_expression_list(TokenType.RBRACKET))

    def parse_hash_literal(self) -> Optional[HashLiteral]:
        pairs: Dict[Expression, Expression] = {}
        while self.peek_token.type != TokenType.RBRACE:
            self.next_token()
            key = self.parse_expression(OperatorPrecedence.LOWEST)

            if not self.expect_peek(TokenType.COLON):
                return None

            self.next_token()
            value = self.parse_expression(OperatorPrecedence.LOWEST)

            pairs[key] = value

            if self.peek_token.type != TokenType.RBRACE and not self.expect_peek(TokenType.COMMA):
                return None

        if not self.expect_peek(TokenType.RBRACE):
            return None

        return HashLiteral(pairs)

    def parse_identifier(self) -> Expression:
        return Identifier(self.current_token.literal)

    def parse_integer_literal(self) -> IntegerLiteral:
        # TODO Error Handling - See Book
        return IntegerLiteral(int(self.current_token.literal))

    def parse_string_literal(self) -> StringLiteral:
        return StringLiteral(self.current_token.literal)

    def parse_boolean_literal(self) -> BooleanLiteral:
        # TODO Error Handling - See Book
        return BooleanLiteral(self.current_token.literal == "true")

    def parse_grouped_expression(self) -> Optional[Expression]:
        self.next_token()
        expression = self.parse_expression(OperatorPrecedence.LOWEST)
        if self.expect_peek(TokenType.RPAREN):
            return expression

    def parse_prefix_expression(self) -> PrefixExpression:
        operator = self.current_token.literal
        self.next_token()
        expression = self.parse_expression(OperatorPrecedence.PREFIX)
        return PrefixExpression(operator, expression)

    def parse_infix_expression(self, left: Expression) -> InfixExpression:
        operator = self.current_token.literal
        precedence = self.current_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        return InfixExpression(left, operator, right)

    def parse_call_expression(self, left: Union[Identifier, FunctionLiteral]) -> CallExpression:
        return CallExpression(left, self.parse_expression_list(TokenType.RPAREN))

    def parse_index_expression(self, left: Expression) -> Optional[IndexExpression]:
        self.next_token()
        index = self.parse_expression(OperatorPrecedence.LOWEST)
        if not self.expect_peek(TokenType.RBRACKET):
            return None
        return IndexExpression(left, index)

    def parse_expression(self, precedence: OperatorPrecedence):
        if (prefix_fn := self.prefix_parse_fns.get(self.current_token.type)) is None:
            return None
        left = prefix_fn()
        while self.peek_token.type != TokenType.SEMICOLON and precedence < self.peek_precedence():
            if (infix := self.infix_parse_fns.get(self.peek_token.type)) is None:
                return left
            self.next_token()
            left = infix(left)
        return left

    def parse_expression_statement(self) -> Optional[ExpressionStatement]:
        statement = ExpressionStatement(self.parse_expression(OperatorPrecedence.LOWEST))
        # Ending a statement with a semicolon is optional
        if self.peek_token.type == TokenType.SEMICOLON:
            self.next_token()
        return statement
