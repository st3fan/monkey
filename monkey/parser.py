

from enum import IntEnum
from typing import Callable, Dict, List, Optional, TypeAlias

from monkey.ast import BooleanLiteral, ExpressionStatement, InfixExpression, IntegerLiteral, PrefixExpression, Program, Statement, LetStatement, IfStatement, ReturnStatement, Expression, Identifier
from monkey.lexer import Lexer
from monkey.token import Token, TokenType


class ExpressionPrecedence(IntEnum):
    LOWEST = 0
    EQUALS = 1          # ==
    LESSGREATER = 2     # > or <
    SUM = 3             # +
    PRODUCT = 4         # *
    PREFIX = 5          # -X or !X
    CALL = 6            # myFunction(X)


TOKEN_PRECEDENCES = {
    TokenType.EQ:       ExpressionPrecedence.EQUALS,
    TokenType.NOT_EQ:   ExpressionPrecedence.EQUALS,
    TokenType.LT:       ExpressionPrecedence.LESSGREATER,
    TokenType.GT:       ExpressionPrecedence.LESSGREATER,
    TokenType.PLUS:     ExpressionPrecedence.SUM,
    TokenType.MINUS:    ExpressionPrecedence.SUM,
    TokenType.SLASH:    ExpressionPrecedence.PRODUCT,
    TokenType.ASTERISK: ExpressionPrecedence.PRODUCT,
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
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.BANG: self.parse_prefix_expression,
            TokenType.TRUE: self.parse_boolean_literal,
            TokenType.FALSE: self.parse_boolean_literal,
            TokenType.LPAREN: self.parse_grouped_expression,
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

    def peek_precedence(self) -> ExpressionPrecedence:
        return TOKEN_PRECEDENCES.get(self.peek_token.type, ExpressionPrecedence.LOWEST)

    def current_precedence(self) -> ExpressionPrecedence:
        return TOKEN_PRECEDENCES.get(self.current_token.type, ExpressionPrecedence.LOWEST)

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
            case TokenType.IF:
                return self.parse_if_statement()
        return self.parse_expression_statement()

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

    def parse_if_statement(self) -> Optional[IfStatement]:
        return None

    def parse_identifier(self) -> Expression:
        return Identifier(self.current_token.literal)

    def parse_integer_literal(self) -> IntegerLiteral:
        # TODO Error Handling - See Book
        return IntegerLiteral(int(self.current_token.literal))

    def parse_boolean_literal(self) -> BooleanLiteral:
        # TODO Error Handling - See Book
        return BooleanLiteral(self.current_token.literal == "true")

    def parse_grouped_expression(self) -> Optional[Expression]:
        self.next_token()
        expression = self.parse_expression(ExpressionPrecedence.LOWEST)
        if self.expect_peek(TokenType.RPAREN):
            return expression

    def parse_prefix_expression(self) -> PrefixExpression:
        operator = self.current_token.literal
        self.next_token()
        expression = self.parse_expression(ExpressionPrecedence.PREFIX)
        return PrefixExpression(operator, expression)

    def parse_infix_expression(self, left: Expression) -> InfixExpression:
        operator = self.current_token.literal
        precedence = self.current_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        return InfixExpression(left, operator, right)

    def parse_expression(self, precedence: ExpressionPrecedence):
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
        statement = ExpressionStatement(self.parse_expression(ExpressionPrecedence.LOWEST))
        # Ending a statement with a semicolon is optional
        if self.peek_token.type == TokenType.SEMICOLON:
            self.next_token()
        return statement
