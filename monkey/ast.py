

from dataclasses import dataclass, field
from typing import Callable, List, Optional, TypeAlias

from monkey.token import Token, TokenType


# I don't think we really need a base class? Yet? Or maybe not at all? I think this may be useful for common debugging or if we really need to keep a Token around, like to keep track of where in the source input we found this.
# @dataclass
# class Node:
#     pass


@dataclass
class Expression:
    pass


@dataclass
class Identifier(Expression):
    value: str

    def __str__(self):
        return self.value


@dataclass
class IntegerLiteral(Expression):
    value: int

    def __str__(self):
        return str(self.value)


@dataclass
class BooleanLiteral(Expression):
    value: bool

    def __str__(self):
        return str(self.value).lower()


@dataclass
class PrefixExpression(Expression):
    operator: str # TODO Candidate for an Enum?
    right: Expression

    def __str__(self):
        return f"({self.operator}{str(self.right)})"


@dataclass
class InfixExpression(Expression):
    left: Expression
    operator: str
    right: Expression

    def __str__(self):
        return f"({str(self.left)} {self.operator} {str(self.right)})"


@dataclass
class Statement:
    pass


@dataclass
class ExpressionStatement(Statement):
    expression: Expression

    def __str__(self):
        return str(self.expression)


@dataclass
class Program:
    statements: List[Statement] = field(default_factory=list)

    def __str__(self):
        # TODO What is a more idiomatic way?
        s = ""
        for statement in self.statements:
            s += str(statement)
        return s


@dataclass
class LetStatement(Statement):
    name: Identifier
    value: ExpressionStatement

    def __str__(self):
        return f"let {self.name} = {str(self.value)};"


@dataclass
class ReturnStatement(Statement):
    value: ExpressionStatement

    def __str__(self):
        return f"return {str(self.value)};"


@dataclass
class IfStatement(Statement):
    pass
