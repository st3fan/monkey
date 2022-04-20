# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from struct import unpack_from
from typing import List, Optional

from .code import Opcode
from .compiler import Bytecode
from .evaluator import make_boolean, is_truthy
from .object import NULL, Object, Integer, Boolean, TRUE, FALSE


DEFAULT_STACK_SIZE = 2048


class VirtualMachine:
    bytecode: Bytecode
    stack: List[Object]
    stack_size: int
    ip: int
    last: Optional[Object]

    def __init__(self, bytecode: Bytecode, stack_size = DEFAULT_STACK_SIZE):
        self.bytecode = bytecode
        self.stack = []
        self.stack_size = stack_size
        self.ip = 0
        self.last = None

    def push(self, value: Object):
        if len(self.stack) == self.stack_size:
            raise Exception("Stack overflow")
        self.stack.append(value)

    def pop(self) -> Object:
        if len(self.stack) == 0:
            raise Exception("Stack underflow")
        self.last = self.stack.pop()
        return self.last

    def last_popped_object(self) -> Optional[Object]:
        return self.last

    def peek(self) -> Optional[Object]:
        if len(self.stack) == 0:
            return None
        return self.stack[-1]

    def read_opcode(self) -> Opcode:
        opcode = Opcode(self.bytecode.instructions[self.ip])
        self.ip += 1
        return opcode

    def read_ushort(self) -> int:
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
                self.push(make_boolean(left == right))
            case (left, Opcode.NOT_EQUAL, right):
                self.push(make_boolean(left != right))
            case (Integer(left_value), _, Integer(right_value)):
                match opcode:
                    case Opcode.LESS_THAN:
                        return self.push(make_boolean(left_value < right_value))
                    case Opcode.GREATER_THAN:
                        return self.push(make_boolean(left_value > right_value))
            case (Boolean(left_value), _, Boolean(right_value)):
                raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")

    def execute_constant(self):
        operand = self.read_ushort()
        self.push(self.bytecode.constants[operand])

    def execute_minus(self):
        operand = self.pop()
        if not isinstance(operand, Integer):
            raise Exception(f"unsupported type for negation: {operand.type()}")
        self.push(Integer(-operand.value))

    def execute_bang(self):
        operand = self.pop()
        self.push(make_boolean(not is_truthy(operand)))

    def run(self):
        self.ip = 0
        while self.ip < len(self.bytecode.instructions):
            opcode = self.read_opcode()
            match opcode:
                case Opcode.CONSTANT:
                    self.execute_constant()
                case Opcode.POP:
                    self.a = self.pop()
                case Opcode.ADD | Opcode.SUBTRACT | Opcode.MULTIPLY | Opcode.DIVIDE:
                    self.execute_binary_operation(opcode)
                case Opcode.EQUAL | Opcode.NOT_EQUAL | Opcode.LESS_THAN | Opcode.GREATER_THAN:
                    self.execute_comparison(opcode)
                case Opcode.MINUS:
                    self.execute_minus()
                case Opcode.BANG:
                    self.execute_bang()
                case Opcode.TRUE:
                    self.push(TRUE)
                case Opcode.FALSE:
                    self.push(FALSE)
                case opcode.JUMP:
                    position = self.read_ushort()
                    self.ip = position
                case opcode.JUMP_NOT_TRUTHY:
                    position = self.read_ushort()
                    if not is_truthy(self.pop()):
                        self.ip = position
                case opcode.NULL:
                    self.push(NULL)
                case _:
                    raise Exception(f"unhandled opcode: {opcode}")
