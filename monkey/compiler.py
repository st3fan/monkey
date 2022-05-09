# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from enum import Enum
from gzip import READ
from typing import Dict, List, Optional

from .ast import *
from .builtins import BUILTINS
from .code import Opcode, make
from .object import CompiledFunction, Object, Integer, String


@dataclass
class EmittedInstruction:
    opcode: Opcode
    position: int


@dataclass
class Bytecode:
    instructions: bytes
    constants: List[Object]


class SymbolScope(Enum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"
    BUILTIN = "BUILTIN"
    FREE = "FREE"
    FUNCTION = "FUNCTION" # TODO This feels like hack.


@dataclass
class Symbol:
    name: str
    scope: SymbolScope
    index: int


@dataclass
class SymbolTable:
    outer: Optional["SymbolTable"] = field(default=None)
    store: Dict[str, Symbol] = field(default_factory=dict)
    free_symbols: List[Symbol] = field(default_factory=list)
    next_index: int = 0

    def define(self, name: str) -> Symbol:
        # if name in self.store:
        #     return self.store[name] # TODO Assuming we want this .. not sure?
        symbol = Symbol(name, SymbolScope.GLOBAL if self.outer is None else SymbolScope.LOCAL, self.next_index)
        self.next_index += 1
        self.store[name] = symbol
        return symbol

    # TODO There is some ambiguity here. Index is either in BUILTINS or in self.store.
    def define_builtin(self, index: int, name: str) -> Symbol:
        if self.outer is not None:
            raise Exception("builtins can only be defined in the global symbol table")
        symbol = Symbol(name, SymbolScope.BUILTIN, index)
        self.store[name] = symbol
        return symbol

    def _define_free(self, original_symbol: Symbol) -> Symbol:
        self.free_symbols.append(original_symbol)
        symbol = Symbol(original_symbol.name, SymbolScope.FREE, len(self.free_symbols) - 1)
        self.store[original_symbol.name] = symbol
        return symbol

    def define_function_name(self, function_name: str) -> Symbol:
        symbol = Symbol(function_name, SymbolScope.FUNCTION, 0)
        self.store[function_name] = symbol
        return symbol

    # TODO This can be more Pythonic
    def resolve(self, name: str) -> Optional[Symbol]:
        obj = self.store.get(name)
        if obj is None and self.outer is not None:
            obj = self.outer.resolve(name)
            if not obj:
                return None
            if obj.scope in (SymbolScope.GLOBAL, SymbolScope.BUILTIN):
                return obj
            return self._define_free(obj)
        return obj

@dataclass
class CompilationScope:
    instructions: bytearray = field(default_factory=bytearray)
    last_instruction: Optional[EmittedInstruction] = field(default=None)
    prev_instruction: Optional[EmittedInstruction] = field(default=None)


@dataclass
class CompilerState:
    symbol_table: SymbolTable = SymbolTable()
    constants: List[Object] = field(default_factory=list)


# TODO self.scopes[self.scope_index] can be much shorter


class Compiler:
    state: CompilerState
    scopes: List[CompilationScope]
    scope_index: int
    symbol_table: SymbolTable

    def __init__(self, state: Optional[CompilerState] = None):
        self.state = state if state else CompilerState()
        self.symbol_table = state.symbol_table if state else SymbolTable()
        self.scopes = [CompilationScope()]
        self.scope_index = 0

        # TODO Would be nicer to index builtins by name instead of index
        for builtin_index, builtin in enumerate(BUILTINS):
            self.symbol_table.define_builtin(builtin_index, builtin.name)

    def enter_scope(self):
        self.scopes.append(CompilationScope())
        self.scope_index += 1
        self.symbol_table = SymbolTable(self.symbol_table)

    def leave_scope(self) -> bytes:
        assert self.scope_index != 0
        scope = self.scopes.pop()
        self.scope_index -= 1
        if self.symbol_table.outer is None:
            raise Exception("Internal compiler error: self.symbol_table.outer is None")
        self.symbol_table = self.symbol_table.outer
        return scope.instructions

    def add_constant(self, constant: Union[Integer, String, CompiledFunction]) -> int:
        self.state.constants.append(constant)
        return len(self.state.constants) - 1

    def add_instruction(self, instruction: bytes) -> int:
        pos = len(self.scopes[self.scope_index].instructions)
        self.scopes[self.scope_index].instructions += instruction # This works but is weird - should we just use bytes() ? Or an Alias?
        return pos

    def set_last_instruction(self, opcode: Opcode, position: int):
        self.scopes[self.scope_index].prev_instruction = self.scopes[self.scope_index].last_instruction
        self.scopes[self.scope_index].last_instruction = EmittedInstruction(opcode, position)

    # TODO I really don't like any of this stuff around POP
    def last_instruction_is_pop(self) -> bool:
        return self.scopes[self.scope_index].last_instruction is not None and self.scopes[self.scope_index].last_instruction.opcode == Opcode.POP

    def last_instruction_is_return_value(self) -> bool:
        return self.scopes[self.scope_index].last_instruction is not None and self.scopes[self.scope_index].last_instruction.opcode == Opcode.RETURN_VALUE

    def remove_last_pop(self):
        assert self.scopes[self.scope_index].last_instruction is not None # TODO ???
        self.scopes[self.scope_index].instructions = self.scopes[self.scope_index].instructions[:self.scopes[self.scope_index].last_instruction.position]
        self.scopes[self.scope_index].last_instruction = self.scopes[self.scope_index].prev_instruction

    def replace_instruction(self, position: int, new_instruction: bytes):
        self.scopes[self.scope_index].instructions[position:position+len(new_instruction)] = new_instruction

    def replace_last_pop_with_return_value(self):
        last_pos = self.scopes[self.scope_index].last_instruction.position
        self.replace_instruction(last_pos, make(Opcode.RETURN_VALUE))
        self.scopes[self.scope_index].last_instruction.opcode = Opcode.RETURN_VALUE

    def change_operand(self, position: int, operand: int):
        opcode = Opcode(int(self.scopes[self.scope_index].instructions[position]))
        new_instruction = make(opcode, [operand])
        self.replace_instruction(position, new_instruction)

    # TODO Are there actually opcodes with multiple operands? If not then we can simplify this.
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

        after_consequence_pos = len(self.scopes[self.scope_index].instructions)
        self.change_operand(jump_not_truthy_pos, after_consequence_pos)

        if not node.alternative:
            self.emit(Opcode.NULL)
        else:
            self.compile(node.alternative)
            if self.last_instruction_is_pop():
                self.remove_last_pop()
        after_alternative_pos = len(self.scopes[self.scope_index].instructions)
        self.change_operand(jump_pos, after_alternative_pos)

    def compile_expression_statement(self, node: ExpressionStatement):
        self.compile(node.expression)
        self.emit(Opcode.POP)

    def compile_array_literal(self, node: ArrayLiteral):
        for element in node.elements:
            self.compile(element)
        self.emit(Opcode.ARRAY, [len(node.elements)])

    def compile_hash_literal(self, node: HashLiteral):
        for key, value in node.pairs.items():
            self.compile(key)
            self.compile(value)
        self.emit(Opcode.HASH, [len(node.pairs)])

    def compile_function_literal(self, node: FunctionLiteral):
        self.enter_scope()

        if function_name := node.name:
            self.symbol_table.define_function_name(function_name)

        # Define the function parameters
        for parameter in node.parameters:
            self.symbol_table.define(parameter.value)

        self.compile(node.body)

        if self.last_instruction_is_pop():
            self.replace_last_pop_with_return_value()

        if not self.last_instruction_is_return_value():
            self.emit(Opcode.RETURN)

        free_symbols = self.symbol_table.free_symbols
        num_locals = self.symbol_table.next_index # TODO Is NumDefinitions in the book
        instructions = self.leave_scope()

        for s in free_symbols:
            self.load_symbol(s)

        compiled_function = CompiledFunction(instructions, num_locals, len(node.parameters))
        self.emit(Opcode.CLOSURE, [self.add_constant(compiled_function), len(free_symbols)])

    def compile_return_statement(self, node: ReturnStatement):
        self.compile(node.return_value)
        self.emit(Opcode.RETURN_VALUE)

    def compile_call_expression(self, node: CallExpression):
        self.compile(node.function)
        for argument in node.arguments:
            self.compile(argument)
        self.emit(Opcode.CALL, [len(node.arguments)])

    def compile_let_statement(self, node: LetStatement):
        symbol = self.symbol_table.define(node.name.value)
        self.compile(node.value)
        self.emit(Opcode.SET_GLOBAL if symbol.scope == SymbolScope.GLOBAL else Opcode.SET_LOCAL, [symbol.index])

    def load_symbol(self, symbol: Symbol):
        match symbol.scope:
            case SymbolScope.GLOBAL:
                self.emit(Opcode.GET_GLOBAL, [symbol.index])
            case SymbolScope.LOCAL:
                self.emit(Opcode.GET_LOCAL, [symbol.index])
            case SymbolScope.BUILTIN:
                self.emit(Opcode.GET_BUILTIN, [symbol.index])
            case SymbolScope.FREE:
                self.emit(Opcode.GET_FREE, [symbol.index])
            case SymbolScope.FUNCTION:
                self.emit(Opcode.CURRENT_CLOSURE)

    def compile(self, node: Node):
        match node:
            case Program():
                for statement in node.statements:
                    self.compile(statement)
            case BlockStatement():
                for statement in node.statements:
                    self.compile(statement)
            case LetStatement():
                self.compile_let_statement(node)
            case Identifier():
                if (symbol := self.symbol_table.resolve(node.value)) is None:
                    raise Exception(f"undefined variable or builtin: {node.value}")
                return self.load_symbol(symbol)
            case IntegerLiteral():
                integer = Integer(node.value)
                self.emit(Opcode.CONSTANT, [self.add_constant(integer)])
            case StringLiteral():
                string = String(node.value)
                self.emit(Opcode.CONSTANT, [self.add_constant(string)])
            case ArrayLiteral():
                self.compile_array_literal(node)
            case HashLiteral():
                self.compile_hash_literal(node)
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
            case IndexExpression():
                self.compile(node.left)
                self.compile(node.index)
                self.emit(Opcode.INDEX)
            case IfExpression():
                self.compile_if_expression(node)
            case ExpressionStatement():
                self.compile_expression_statement(node)
            case FunctionLiteral():
                self.compile_function_literal(node)
            case ReturnStatement():
                self.compile_return_statement(node)
            case CallExpression():
                self.compile_call_expression(node)
            case _:
                raise Exception(f"unknown node {node.__class__.__name__}")

    def bytecode(self) -> Bytecode:
        assert self.scope_index == 0 # TODO Right?
        return Bytecode(self.scopes[self.scope_index].instructions, self.state.constants)
