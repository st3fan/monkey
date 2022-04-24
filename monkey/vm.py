# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from struct import unpack_from
from typing import List, Optional

from .code import Opcode
from .compiler import Bytecode
from .evaluator import make_boolean, is_truthy
from .object import Array, CompiledFunction, Hash, Object, Integer, Boolean, TRUE, FALSE, NULL, String


DEFAULT_STACK_SIZE = 2048
DEFAULT_GLOBALS_SIZE = 65536
DEFAULT_MAX_FRAMES = 1024


@dataclass
class Frame:
    fn: CompiledFunction
    ip: int = field(default=-1)


@dataclass
class VirtualMachineState:
    globals: List[Object] = field(init=False)

    def __post_init__(self):
        self.globals = [NULL] * DEFAULT_GLOBALS_SIZE


class VirtualMachine:
    constants: List[Object]
    stack: List[Object]
    frames: List[Frame]
    globals: List[Object]
    last: Optional[Object] # TODO Would be nice to get rid of this. Only exists for REPL.

    def __init__(self, bytecode: Bytecode, state: Optional[VirtualMachineState] = None):
        self.constants = bytecode.constants
        self.stack = []
        self.globals = state.globals if state else [NULL] * DEFAULT_GLOBALS_SIZE
        self.frames = [Frame(CompiledFunction(bytecode.instructions))]
        self.last = None

    def current_frame(self):
        assert len(self.frames) != 0
        return self.frames[-1]

    def push_frame(self, frame: Frame):
        self.frames.append(frame)

    def pop_frame(self) -> Frame:
        assert len(self.frames) != 0
        return self.frames.pop()

    def push(self, value: Object):
        if len(self.stack) == DEFAULT_STACK_SIZE:
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

    def read_ushort(self) -> int:
        (constant_index,) = unpack_from(">H", self.current_frame().fn.instructions, self.current_frame().ip+1)
        self.current_frame().ip += 2
        return constant_index

    def execute_binary_operation(self, opcode: Opcode):
        right, left = self.pop(), self.pop()
        match (left, opcode, right):
            case (String(left_value), Opcode.ADD, String(right_value)):
                self.push(String(left_value + right_value))
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
            case (String(left_value), _, String(right_value)):
                match opcode:
                    case Opcode.LESS_THAN:
                        return self.push(make_boolean(left_value < right_value))
                    case Opcode.GREATER_THAN:
                        return self.push(make_boolean(left_value > right_value))
                    case _:
                        raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")
            case (Integer(left_value), _, Integer(right_value)):
                match opcode:
                    case Opcode.LESS_THAN:
                        return self.push(make_boolean(left_value < right_value))
                    case Opcode.GREATER_THAN:
                        return self.push(make_boolean(left_value > right_value))
                    case _:
                        raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")
            case (Boolean(left_value), _, Boolean(right_value)):
                raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")

    def execute_constant(self):
        operand = self.read_ushort()
        self.push(self.constants[operand])

    def execute_minus(self):
        operand = self.pop()
        if not isinstance(operand, Integer):
            raise Exception(f"unsupported type for negation: {operand.type()}")
        self.push(Integer(-operand.value))

    def execute_bang(self):
        operand = self.pop()
        self.push(make_boolean(not is_truthy(operand)))

    def execute_index_expression(self):
        index = self.pop()
        container = self.pop()
        match container, index:
            case Array(elements), Integer(index_value):
                if index_value < 0 or index_value > len(elements)-1:
                    self.push(NULL)
                else:
                    self.push(elements[index_value])
            case Hash(pairs), index:
                self.push(pairs.get(index, NULL))
            case _:
                raise Exception(f"index operator not supported: {container.type()}")

    def run(self):
        while self.current_frame().ip < len(self.current_frame().fn.instructions)-1:
            self.current_frame().ip += 1

            ip = self.current_frame().ip
            opcode = Opcode(self.current_frame().fn.instructions[ip])

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
                case Opcode.JUMP:
                    position = self.read_ushort()
                    self.current_frame().ip = position - 1
                case Opcode.JUMP_NOT_TRUTHY:
                    position = self.read_ushort()
                    if not is_truthy(self.pop()):
                        self.current_frame().ip = position - 1
                case Opcode.NULL:
                    self.push(NULL)
                case Opcode.SET_GLOBAL:
                    global_index = self.read_ushort()
                    self.globals[global_index] = self.pop()
                case Opcode.GET_GLOBAL:
                    global_index = self.read_ushort()
                    self.push(self.globals[global_index])
                case Opcode.ARRAY:
                    array_length = self.read_ushort()
                    elements = list([self.pop() for _ in range(array_length)]) # Ewwwww
                    elements.reverse()
                    self.push(Array(elements))
                case Opcode.HASH:
                    hash_length = self.read_ushort()
                    hash = Hash()
                    for _ in range(hash_length):
                        value = self.pop()
                        key = self.pop()
                        hash.pairs[key] = value
                    self.push(hash)
                case Opcode.INDEX:
                    self.execute_index_expression()
                case _:
                    raise Exception(f"unhandled opcode: {opcode}")
