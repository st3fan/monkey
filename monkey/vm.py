# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from struct import unpack_from
from typing import List, Optional, Union, get_args, get_origin

from .builtins import BUILTINS
from .code import Opcode
from .compiler import Bytecode
from .evaluator import make_boolean, is_truthy
from .object import Array, Builtin, Closure, CompiledFunction, Hash, Object, Integer, Boolean, TRUE, FALSE, NULL, String


DEFAULT_STACK_SIZE = 2048
DEFAULT_GLOBALS_SIZE = 65536
DEFAULT_MAX_FRAMES = 1024


@dataclass
class Frame:
    cl: Closure
    bp: int
    ip: int = field(default=-1)

    def instructions(self) -> bytes:
        return self.cl.fn.instructions


@dataclass
class VirtualMachineState:
    globals: List[Object] = field(init=False)

    def __post_init__(self):
        self.globals = [NULL] * DEFAULT_GLOBALS_SIZE


class VirtualMachine:
    # TODO What is the proper way to setup an object with types? Should this be a dataclass?
    constants: List[Object]
    stack: List[Object]
    sp: int
    frames: List[Frame]
    globals: List[Object]
    last: Optional[Object] # TODO Would be nice to get rid of this. Only exists for REPL.

    def __init__(self, bytecode: Bytecode, state: Optional[VirtualMachineState] = None):
        self.constants = bytecode.constants
        self.stack = [NULL] * DEFAULT_STACK_SIZE
        self.sp = 0
        self.globals = state.globals if state else [NULL] * DEFAULT_GLOBALS_SIZE
        main_function = CompiledFunction(bytecode.instructions, 0, 0)
        main_closure = Closure(fn=main_function, free=[])
        main_frame = Frame(main_closure, 0)
        self.frames = [main_frame]
        self.last = None

    def current_frame(self):
        assert len(self.frames) != 0
        return self.frames[-1]

    def push_frame(self, frame: Frame):
        self.frames.append(frame)

    def pop_frame(self) -> Frame:
        assert len(self.frames) != 0
        return self.frames.pop()

    def push_stack(self, value: Object):
        if self.sp == DEFAULT_STACK_SIZE:
            raise Exception("Stack overflow")
        self.stack[self.sp] = value
        self.sp += 1

    def pop_stack(self) -> Object:
        if self.sp == 0:
            raise Exception("Stack underflow")
        self.last = self.stack[self.sp - 1] # TODO We also need to NULL the element otherwise it sticks around
        self.sp -= 1
        return self.last

    def peek_stack(self) -> Optional[Object]:
        if self.sp > 0:
            return self.stack[self.sp - 1]

    def last_popped_object(self) -> Optional[Object]:
        return self.last

    def read_ushort(self) -> int:
        (value,) = unpack_from(">H", self.current_frame().cl.fn.instructions, self.current_frame().ip+1)
        self.current_frame().ip += 2
        return value

    def read_ubyte(self) -> int:
        (value,) = unpack_from(">B", self.current_frame().cl.fn.instructions, self.current_frame().ip+1)
        self.current_frame().ip += 1
        return value

    def execute_binary_operation(self, opcode: Opcode):
        right, left = self.pop_stack(), self.pop_stack()
        match (left, opcode, right):
            case (String(left_value), Opcode.ADD, String(right_value)):
                self.push_stack(String(left_value + right_value))
            case (Integer(left_value), Opcode.ADD, Integer(right_value)):
                self.push_stack(Integer(left_value + right_value))
            case (Integer(left_value), Opcode.SUBTRACT, Integer(right_value)):
                self.push_stack(Integer(left_value - right_value))
            case (Integer(left_value), Opcode.MULTIPLY, Integer(right_value)):
                self.push_stack(Integer(left_value * right_value))
            case (Integer(left_value), Opcode.DIVIDE, Integer(right_value)):
                self.push_stack(Integer(left_value // right_value))
            case _:
                raise Exception(f"unsupported types for binary operation: {left.type()} {right.type()}")

    def execute_comparison(self, opcode: Opcode):
        right, left = self.pop_stack(), self.pop_stack()
        match (left, opcode, right):
            case (left, Opcode.EQUAL, right):
                self.push_stack(make_boolean(left == right))
            case (left, Opcode.NOT_EQUAL, right):
                self.push_stack(make_boolean(left != right))
            case (String(left_value), _, String(right_value)):
                match opcode:
                    case Opcode.LESS_THAN:
                        return self.push_stack(make_boolean(left_value < right_value))
                    case Opcode.GREATER_THAN:
                        return self.push_stack(make_boolean(left_value > right_value))
                    case _:
                        raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")
            case (Integer(left_value), _, Integer(right_value)):
                match opcode:
                    case Opcode.LESS_THAN:
                        return self.push_stack(make_boolean(left_value < right_value))
                    case Opcode.GREATER_THAN:
                        return self.push_stack(make_boolean(left_value > right_value))
                    case _:
                        raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")
            case (Boolean(left_value), _, Boolean(right_value)):
                raise Exception(f"unknown operator: {opcode.name} ({left.type()} {right.type()})")

    def execute_constant(self):
        operand = self.read_ushort()
        self.push_stack(self.constants[operand])

    def execute_minus(self):
        operand = self.pop_stack()
        if not isinstance(operand, Integer):
            raise Exception(f"unsupported type for negation: {operand.type()}")
        self.push_stack(Integer(-operand.value))

    def execute_bang(self):
        operand = self.pop_stack()
        self.push_stack(make_boolean(not is_truthy(operand)))

    def execute_index_expression(self):
        index = self.pop_stack()
        container = self.pop_stack()
        match container, index:
            case Array(elements), Integer(index_value):
                if index_value < 0 or index_value > len(elements)-1:
                    self.push_stack(NULL)
                else:
                    self.push_stack(elements[index_value])
            case Hash(pairs), index:
                self.push_stack(pairs.get(index, NULL))
            case _:
                raise Exception(f"index operator not supported: {container.type()}")

    # def call_compiled_function(self, function: CompiledFunction, num_arguments: int):
    #     if function.num_parameters != num_arguments:
    #         raise Exception(f"wrong number of arguments: want={function.num_parameters}, got={num_arguments}")
    #     frame = Frame(function, self.sp - num_arguments)
    #     self.push_frame(frame)
    #     self.sp = frame.bp + function.num_locals

    def call_builtin(self, builtin: Builtin, num_arguments: int):
        if len(builtin.argument_types) != num_arguments:
            raise Exception(f"wrong number of arguments. got={num_arguments}, want={len(builtin.argument_types)}")

        arguments = self.stack[self.sp - num_arguments : self.sp]
        for arg, typ in zip(arguments, builtin.argument_types):
            # Check if the argument matches the expected type, taking Union into account too.
            if not ((get_origin(typ) is Union and isinstance(arg, get_args(typ))) or isinstance(arg, typ)):
                if get_origin(typ) is Union:
                    raise Exception(f"argument to `{builtin.name}` not supported, got {arg.type()}")
                else:
                    raise Exception(f"argument to `{builtin.name}` must be {typ.type()}, got {arg.type()}")

        result = builtin.callable(*arguments)
        self.sp = self.sp - num_arguments - 1
        self.push_stack(result)

    def call_closure(self, closure: Closure, num_arguments: int):
        if closure.fn.num_parameters != num_arguments:
            raise Exception(f"wrong number of arguments: want={closure.fn.num_parameters}, got={num_arguments}")
        frame = Frame(closure, self.sp - num_arguments)
        self.push_frame(frame)
        self.sp = frame.bp + closure.fn.num_locals

    def execute_call(self):
        num_args = self.read_ubyte()
        callee = self.stack[self.sp - 1 - num_args]
        match callee:
            case Closure():
                self.call_closure(callee, num_args)
            case Builtin():
                self.call_builtin(callee, num_args)
            case _:
                raise Exception("calling non-closure and non-builtin")

    def execute_return_value(self):
        return_value = self.pop_stack()
        frame = self.pop_frame() # Remove the frame used for this function call
        self.sp = frame.bp - 1 # TODO This keeps references around. Need to NULL?
        self.push_stack(return_value) # Push the return value back on the stack for the caller

    def execute_return(self):
        frame = self.pop_frame() # Remove the frame used for this function call
        self.sp = frame.bp - 1 # TODO This keeps references around. Need to NULL?
        self.push_stack(NULL) # Push a NULL

    def push_closure(self, const_index: int, num_free_variables: int):
        constant = self.constants[const_index]
        if not isinstance(constant, CompiledFunction):
            raise Exception(f"not a function: {constant}")

        free_variables = []
        for i in range(num_free_variables):
            free_variables.append(self.stack[self.sp-num_free_variables+i])
        self.sp = self.sp - num_free_variables

        closure = Closure(constant, free_variables)
        self.push_stack(closure)

    def run(self):
        while self.current_frame().ip < len(self.current_frame().cl.fn.instructions)-1:
            self.current_frame().ip += 1

            ip = self.current_frame().ip
            opcode = Opcode(self.current_frame().cl.fn.instructions[ip])

            match opcode:
                case Opcode.CONSTANT:
                    self.execute_constant()
                case Opcode.POP:
                    self.a = self.pop_stack()
                case Opcode.ADD | Opcode.SUBTRACT | Opcode.MULTIPLY | Opcode.DIVIDE:
                    self.execute_binary_operation(opcode)
                case Opcode.EQUAL | Opcode.NOT_EQUAL | Opcode.LESS_THAN | Opcode.GREATER_THAN:
                    self.execute_comparison(opcode)
                case Opcode.MINUS:
                    self.execute_minus()
                case Opcode.BANG:
                    self.execute_bang()
                case Opcode.TRUE:
                    self.push_stack(TRUE)
                case Opcode.FALSE:
                    self.push_stack(FALSE)
                case Opcode.JUMP:
                    position = self.read_ushort()
                    self.current_frame().ip = position - 1
                case Opcode.JUMP_NOT_TRUTHY:
                    position = self.read_ushort()
                    if not is_truthy(self.pop_stack()):
                        self.current_frame().ip = position - 1
                case Opcode.NULL:
                    self.push_stack(NULL)
                case Opcode.SET_GLOBAL:
                    global_index = self.read_ushort()
                    self.globals[global_index] = self.pop_stack()
                case Opcode.GET_GLOBAL:
                    global_index = self.read_ushort()
                    self.push_stack(self.globals[global_index])
                case Opcode.SET_LOCAL:
                    local_index = self.read_ubyte()
                    frame = self.current_frame()
                    self.stack[frame.bp + local_index] = self.pop_stack()
                case Opcode.GET_LOCAL:
                    local_index = self.read_ubyte()
                    frame = self.current_frame()
                    self.push_stack(self.stack[frame.bp + local_index])
                case Opcode.GET_BUILTIN:
                    builtin_index = self.read_ubyte()
                    self.push_stack(BUILTINS[builtin_index])
                case Opcode.GET_FREE:
                    free_index = self.read_ubyte()
                    current_closure = self.current_frame().cl
                    self.push_stack(current_closure.free[free_index])
                case Opcode.ARRAY:
                    array_length = self.read_ushort()
                    elements = list([self.pop_stack() for _ in range(array_length)]) # Ewwwww
                    elements.reverse()
                    self.push_stack(Array(elements))
                case Opcode.HASH:
                    hash_length = self.read_ushort()
                    hash = Hash()
                    for _ in range(hash_length):
                        value = self.pop_stack()
                        key = self.pop_stack()
                        hash.pairs[key] = value
                    self.push_stack(hash)
                case Opcode.INDEX:
                    self.execute_index_expression()
                case Opcode.CALL:
                    self.execute_call()
                case Opcode.CLOSURE:
                    const_index = self.read_ushort()
                    num_free_variables = self.read_ubyte()
                    self.push_closure(const_index, num_free_variables)
                case Opcode.CURRENT_CLOSURE:
                    current_closure = self.current_frame().cl
                    self.push_stack(current_closure)
                case Opcode.RETURN_VALUE:
                    self.execute_return_value()
                case Opcode.RETURN:
                    self.execute_return()
                case _:
                    raise Exception(f"unhandled opcode: {opcode}")
