# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass
from typing import List, Optional

from .ast import BlockStatement, BooleanLiteral, IfExpression, Node, Program, ExpressionStatement, InfixExpression, IntegerLiteral, PrefixExpression
from .code import Opcode, make
from .object import Object, Integer


@dataclass
class EmittedInstruction:
    opcode: Opcode
    position: int


@dataclass
class Bytecode:
    instructions: bytes
    constants: List[Object]


class Compiler:
    instructions: bytearray
    constants: List[Object]

    last_instruction: Optional[EmittedInstruction]
    prev_instruction: Optional[EmittedInstruction]

    def __init__(self):
        self.instructions = bytearray()
        self.constants = []
        self.last_instruction = None
        self.prev_instruction = None

    def add_constant(self, object: Object) -> int:
        self.constants.append(object)
        return len(self.constants) - 1

    def add_instruction(self, instruction: bytes) -> int:
        pos = len(self.instructions)
        self.instructions += instruction # This works but is weird - should we just use bytes() ? Or an Alias?
        return pos

    def set_last_instruction(self, opcode: Opcode, position: int):
        self.prev_instruction = self.last_instruction
        self.last_instruction = EmittedInstruction(opcode, position)

    # TODO I really don't like any of this stuff around POP
    def last_instruction_is_pop(self) -> bool:
        return self.last_instruction is not None and self.last_instruction.opcode == Opcode.POP

    def remove_last_pop(self):
        self.instructions = self.instructions[:self.last_instruction.position]
        self.last_instruction = self.prev_instruction

    def replace_instruction(self, position: int, new_instruction: bytes):
        self.instructions[position:position+len(new_instruction)] = new_instruction

    def change_operand(self, position: int, operand: int):
        opcode = Opcode(int(self.instructions[position]))
        new_instruction = make(opcode, [operand])
        self.replace_instruction(position, new_instruction)

    def emit(self, opcode: Opcode, operands: List[int] = []) -> int:
        instruction = make(opcode, operands)
        position = self.add_instruction(instruction)
        self.set_last_instruction(opcode, position)
        return position

    def compile_if_expression(self, node: IfExpression):
        self.compile(node.condition)
        jump_not_truthy_pos = self.emit(Opcode.JUMP_NOT_TRUTHY, [9999])
        self.compile(node.consequence)
        if self.last_instruction_is_pop():
            self.remove_last_pop()
        jump_pos = self.emit(Opcode.JUMP, [9999])

        after_consequence_pos = len(self.instructions)
        self.change_operand(jump_not_truthy_pos, after_consequence_pos)

        if not node.alternative:
            self.emit(Opcode.NULL)
        else:
            self.compile(node.alternative)
            if self.last_instruction_is_pop():
                self.remove_last_pop()
        after_alternative_pos = len(self.instructions)
        self.change_operand(jump_pos, after_alternative_pos)

    def compile(self, node: Node):
        match node:
            case Program():
                for statement in node.statements:
                    self.compile(statement)
            case BlockStatement():
                for statement in node.statements:
                    self.compile(statement)
            case ExpressionStatement():
                self.compile(node.expression)
                self.emit(Opcode.POP)
            case IntegerLiteral():
                integer = Integer(node.value)
                self.emit(Opcode.CONSTANT, [self.add_constant(integer)])
            case BooleanLiteral():
                if node.value:
                    self.emit(Opcode.TRUE)
                else:
                    self.emit(Opcode.FALSE)
            case PrefixExpression():
                self.compile(node.right)
                match node.operator:
                    case "!":
                        self.emit(Opcode.BANG)
                    case "-":
                        self.emit(Opcode.MINUS)
                    case _: # TODO Is this actually possible?
                        raise Exception(f"unknown operator {node.operator}")
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
                    case _: # TODO Is this actually possible?
                        raise Exception(f"unknown operator {node.operator}")
            case IfExpression():
                self.compile_if_expression(node)

    def bytecode(self) -> Bytecode:
        return Bytecode(self.instructions, self.constants)
