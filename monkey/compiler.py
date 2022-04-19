# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass
from typing import List

from .ast import BooleanLiteral, Node, Program, ExpressionStatement, InfixExpression, IntegerLiteral
from .code import Opcode, make
from .object import Object, Integer


@dataclass
class Bytecode:
    instructions: bytes
    constants: List[Object]


class Compiler:
    instructions: bytes
    constants: List[Object]

    def __init__(self):
        self.instructions = bytes()
        self.constants = []

    def add_constant(self, object: Object) -> int:
        self.constants.append(object)
        return len(self.constants) - 1

    def add_instruction(self, instruction: bytes) -> int:
        pos = len(self.instructions)
        self.instructions += instruction # This works but is weird - should we just use bytes() ? Or an Alias?
        return pos

    def emit(self, opcode: Opcode, operands: List[int] = []):
        return self.add_instruction(make(opcode, operands))

    def compile(self, node: Node):
        match node:
            case Program():
                for statement in node.statements:
                    self.compile(statement)
            case ExpressionStatement():
                self.compile(node.expression)
            case InfixExpression():
                self.compile(node.left)
                self.compile(node.right)
                match node.operator:
                    case "+":
                        self.emit(Opcode.ADD)
                    case "-":
                        self.emit(Opcode.SUBTRACT)
                    case "*":
                        self.emit(Opcode.MULTIPLY)
                    case "/":
                        self.emit(Opcode.DIVIDE)
                    case "<":
                        self.emit(Opcode.LESS_THAN)
                    case ">":
                        self.emit(Opcode.GREATER_THAN)
                    case "==":
                        self.emit(Opcode.EQUAL)
                    case "!=":
                        self.emit(Opcode.NOT_EQUAL)
            case IntegerLiteral():
                integer = Integer(node.value)
                self.emit(Opcode.CONSTANT, [self.add_constant(integer)])
            case BooleanLiteral():
                if node.value:
                    self.emit(Opcode.TRUE)
                else:
                    self.emit(Opcode.FALSE)

    def bytecode(self) -> Bytecode:
        return Bytecode(self.instructions, self.constants)
