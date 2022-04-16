# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


@dataclass(frozen = True)
class Node:
    pass


@dataclass(frozen = True)
class Statement(Node):
    pass


@dataclass(frozen = True)
class BlockStatement(Statement):
    statements: List[Statement]

    def __str__(self):
        s = "{ "
        for statement in self.statements:
            s += str(statement)
        s += " }"
        return s


@dataclass(frozen = True)
class Expression(Node): # TODO Is an expression a Node or a Statement?
    pass


@dataclass(frozen = True)
class Identifier(Expression):
    value: str

    def __str__(self):
        return self.value


@dataclass(frozen = True)
class IntegerLiteral(Expression):
    value: int

    def __str__(self):
        return str(self.value)


@dataclass(frozen = True)
class BooleanLiteral(Expression):
    value: bool

    def __str__(self):
        return str(self.value).lower()


@dataclass(frozen = True)
class StringLiteral(Expression):
    value: str

    def __str__(self):
        return '"' + self.value + '"'


@dataclass(frozen = True)
class FunctionLiteral(Expression):
    parameters: List[Identifier]
    body: BlockStatement

    def __str__(self):
        return f"fn ({', '.join(str(p) for p in self.parameters)}) {str(self.body)}"


@dataclass(frozen = True)
class ArrayLiteral(Expression):
    elements: List[Expression]

    def __str__(self):
        return f"[{', '.join(str(e) for e in self.elements)}]"


@dataclass(frozen = True)
class HashLiteral(Expression):
    pairs: Dict[Expression, Expression]

    def __str__(self):
        contents = ""
        for k, v in self.pairs.items():
            if len(contents):
                contents += ", "
            contents += str(k) + ":" + str(v)
        return '{' + contents + '}'


@dataclass(frozen = True)
class IndexExpression(Expression):
    left: Expression
    index: Expression

    def __str__(self):
        return f"({str(self.left)}[{str(self.index)}])"


@dataclass(frozen = True)
class CallExpression(Expression):
    function: Union[Identifier, FunctionLiteral] # TODO NamedCallExpression vs FunctionLiteralCallExpression?
    arguments: List[Expression]

    def __str__(self):
        return f"{str(self.function)}({', '.join(str(p) for p in self.arguments)})"


@dataclass(frozen = True)
class PrefixExpression(Expression):
    operator: str # TODO Candidate for an Enum?
    right: Expression

    def __str__(self):
        return f"({self.operator}{str(self.right)})"


@dataclass(frozen = True)
class InfixExpression(Expression):
    left: Expression
    operator: str
    right: Expression

    def __str__(self):
        return f"({str(self.left)} {self.operator} {str(self.right)})"


@dataclass(frozen = True)
class IfExpression(Expression):
    condition: Expression
    consequence: BlockStatement
    alternative: Optional[BlockStatement]

    def __str__(self):
        s = f"if {str(self.condition)} {str(self.consequence)}"
        if self.alternative:
            s += f" else {str(self.alternative)}"
        return s


@dataclass(frozen = True)
class ExpressionStatement(Statement):
    expression: Expression

    def __str__(self):
        return str(self.expression)


@dataclass(frozen = True)
class Program(Node):
    statements: List[Statement] = field(default_factory=list)

    def __str__(self):
        # TODO What is a more idiomatic way?
        s = ""
        for statement in self.statements:
            s += str(statement)
        return s


@dataclass(frozen = True)
class LetStatement(Statement):
    name: Identifier
    value: ExpressionStatement

    def __str__(self):
        return f"let {self.name} = {str(self.value)};"


@dataclass(frozen = True)
class ReturnStatement(Statement):
    value: ExpressionStatement

    def __str__(self):
        return f"return {str(self.value)};"
