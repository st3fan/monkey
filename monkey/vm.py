# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from struct import unpack_from
from typing import List, Optional

from .code import Opcode
from .compiler import Bytecode
from .object import Object, Integer, Boolean, TRUE, FALSE


DEFAULT_STACK_SIZE = 2048


class VirtualMachine:
    bytecode: Bytecode
    stack: List[Object]
    stack_size: int

    def __init__(self, bytecode: Bytecode, stack_size = DEFAULT_STACK_SIZE):
        self.bytecode = bytecode
        self.stack = []
        self.stack_size = stack_size
        self.ip = 0

    def push(self, value: Object):
        if len(self.stack) == self.stack_size:
            raise Exception("Stack overflow")
        self.stack.append(value)

    def pop(self) -> Object:
        if len(self.stack) == 0:
            raise Exception("Stack underflow")
        return self.stack.pop()

    def peek(self) -> Optional[Object]:
        if len(self.stack) == 0:
            return None
        return self.stack[-1]

    def read_opcode(self) -> Opcode:
        opcode = Opcode(self.bytecode.instructions[self.ip])
        self.ip += 1
        return opcode

    def read_constant_index(self) -> int:
        (constant_index,) = unpack_from(">H", self.bytecode.instructions, self.ip)
        self.ip += 2
        return constant_index

    def execute_binary_operation(self, opcode: Opcode):
        right, left = self.pop(), self.pop()
        match (left, opcode, right):
            case (Integer(left_value), Opcode.ADD, Integer(right_value)):
                self.push(Integer(left_value + right_value))
            case (Integer(left_value), Opcode.SUBTRACT, Integer(right_value)):
                self.push(Integer(left_value - right_value))
            case (Integer(left_value), Opcode.MULTIPLY, Integer(right_value)):
                self.push(Integer(left_value * right_value))
            case (Integer(left_value), Opcode.DIVIDE, Integer(right_value)):
                self.push(Integer(left_value // right_value))
            case _:
                raise Exception(f"unsupported types for binary operation: {left.type()} {right.type()}")

    def execute_comparison(self, opcode: Opcode):
        right, left = self.pop(), self.pop()
        match (left, opcode, right):
            case (left, Opcode.EQUAL, right):
                self.push(TRUE if left == right else FALSE) # TODO In evaluator.py we have make_boolean()
            case (left, Opcode.NOT_EQUAL, right):
                self.push(TRUE if left != right else FALSE)
            case (Integer(left_value), _, Integer(right_value)):
                match opcode:
                    case Opcode.LESS_THAN:
                        return self.push(TRUE if left_value < right_value else FALSE)
                    case Opcode.GREATER_THAN:
                        return self.push(TRUE if left_value > right_value else FALSE)
            case (Boolean(left_value), _, Boolean(right_value)):
                raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")

    def run(self):
        self.ip = 0
        while self.ip < len(self.bytecode.instructions):
            opcode = self.read_opcode()
            match opcode:
                case Opcode.CONSTANT:
                    constant_index = self.read_constant_index()
                    self.push(self.bytecode.constants[constant_index])
                case Opcode.ADD | Opcode.SUBTRACT | Opcode.MULTIPLY | Opcode.DIVIDE:
                    self.execute_binary_operation(opcode)
                case Opcode.EQUAL | Opcode.NOT_EQUAL | Opcode.LESS_THAN | Opcode.GREATER_THAN:
                    self.execute_comparison(opcode)
                case Opcode.TRUE:
                    self.push(TRUE)
                case Opcode.FALSE:
                    self.push(FALSE)
