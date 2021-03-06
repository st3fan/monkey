# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import pytest

from .lexer import Lexer
from .parser import Parser
from .code import Opcode, make
from .compiler import CompilationScope, Compiler, EmittedInstruction
from .object import CompiledFunction, Integer, String


def test_last_instruction_is_pop():
    compiler = Compiler()
    compiler.emit(Opcode.CONSTANT, [0])
    assert compiler.last_instruction_is_pop() == False
    compiler.emit(Opcode.POP)
    assert compiler.last_instruction_is_pop() == True


def test_remove_last_pop():
    compiler = Compiler()
    compiler.emit(Opcode.CONSTANT, [0])
    compiler.emit(Opcode.POP)
    compiler.remove_last_pop()
    assert compiler.scopes[compiler.scope_index].instructions == make(Opcode.CONSTANT, [0])


def test_last_prev_instruction():
    compiler = Compiler()
    assert compiler.scopes[compiler.scope_index].prev_instruction is None
    assert compiler.scopes[compiler.scope_index].last_instruction is None
    compiler.emit(Opcode.CONSTANT, [0])
    assert compiler.scopes[compiler.scope_index].prev_instruction is None
    assert compiler.scopes[compiler.scope_index].last_instruction == EmittedInstruction(Opcode.CONSTANT, 0)
    compiler.emit(Opcode.JUMP_NOT_TRUTHY, [0])
    assert compiler.scopes[compiler.scope_index].prev_instruction == EmittedInstruction(Opcode.CONSTANT, 0)
    assert compiler.scopes[compiler.scope_index].last_instruction == EmittedInstruction(Opcode.JUMP_NOT_TRUTHY, 3)
    compiler.emit(Opcode.JUMP, [0])
    assert compiler.scopes[compiler.scope_index].prev_instruction == EmittedInstruction(Opcode.JUMP_NOT_TRUTHY, 3)
    assert compiler.scopes[compiler.scope_index].last_instruction == EmittedInstruction(Opcode.JUMP, 6)


def test__scopes():
    compiler = Compiler()
    assert compiler.scope_index == 0
    assert compiler.scopes[compiler.scope_index] == CompilationScope()

    global_symbol_table = compiler.symbol_table

    compiler.emit(Opcode.MULTIPLY)
    assert len(compiler.scopes[compiler.scope_index].instructions) == 1

    compiler.enter_scope()
    assert compiler.scope_index == 1
    compiler.emit(Opcode.SUBTRACT)
    assert len(compiler.scopes[compiler.scope_index].instructions) == 1
    assert compiler.scopes[compiler.scope_index].last_instruction.opcode == Opcode.SUBTRACT

    assert compiler.symbol_table.outer == global_symbol_table

    compiler.leave_scope()
    assert compiler.scope_index == 0
    assert compiler.symbol_table == global_symbol_table
    assert compiler.symbol_table.outer is None

    compiler.emit(Opcode.ADD)
    assert len(compiler.scopes[compiler.scope_index].instructions) == 2
    assert compiler.scopes[compiler.scope_index].last_instruction.opcode == Opcode.ADD
    assert compiler.scopes[compiler.scope_index].prev_instruction.opcode == Opcode.MULTIPLY


def test_change_operand():
    compiler = Compiler()
    compiler.emit(Opcode.JUMP, [0x1234])
    assert compiler.scopes[compiler.scope_index].instructions[1] == 0x12
    assert compiler.scopes[compiler.scope_index].instructions[2] == 0x34
    compiler.change_operand(0, 0x5678)
    assert compiler.scopes[compiler.scope_index].instructions[1] == 0x56
    assert compiler.scopes[compiler.scope_index].instructions[2] == 0x78


def test_emit_position():
    compiler = Compiler()
    assert compiler.emit(Opcode.CONSTANT, [0]) == 0
    assert compiler.emit(Opcode.CONSTANT, [0]) == 3
    assert compiler.emit(Opcode.JUMP, [0]) == 6
    assert compiler.emit(Opcode.POP) == 9
    assert compiler.emit(Opcode.JUMP_NOT_TRUTHY, [0]) == 10


def _compile_and_assert(test):
    program = Parser(Lexer(test["expression"])).parse_program()
    compiler = Compiler()
    compiler.compile(program)
    bytecode = compiler.bytecode()
    assert bytecode.instructions == b''.join(test["instructions"])
    assert bytecode.constants == test["constants"]


INTEGER_ARITHMETIC_TESTS = [
    { "expression": "7 + 5",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.ADD),
          make(Opcode.POP) ],
      "constants": [
          Integer(7),
          Integer(5) ] },
    { "expression": "7 - 5",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.SUBTRACT),
          make(Opcode.POP) ],
      "constants": [
          Integer(7),
          Integer(5) ] },
    { "expression": "7 * 5",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.MULTIPLY),
          make(Opcode.POP)
      ],
      "constants": [
          Integer(7),
          Integer(5)
      ] },
    { "expression": "7 * 5",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.MULTIPLY),
          make(Opcode.POP) ],
      "constants": [
          Integer(7),
          Integer(5)
      ] },
    { "expression": "7; 5",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.POP),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.POP) ],
      "constants": [
          Integer(7),
          Integer(5) ] },
]


@pytest.mark.parametrize("test", INTEGER_ARITHMETIC_TESTS)
def test_integer_arithmetic(test):
    _compile_and_assert(test)


BOOLEAN_TESTS = [
    { "expression": "true",
      "instructions": [
          make(Opcode.TRUE),
          make(Opcode.POP) ],
      "constants": [] },
    { "expression": "false",
      "instructions": [
          make(Opcode.FALSE),
          make(Opcode.POP) ],
      "constants": [] },
]


@pytest.mark.parametrize("test", BOOLEAN_TESTS)
def test_booleans_arithmetic(test):
    _compile_and_assert(test)


COMPARISON_OPERATORS_TESTS = [
    { "expression": "1 > 2",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.GREATER_THAN),
          make(Opcode.POP) ],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "1 < 2",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.LESS_THAN),
          make(Opcode.POP) ],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "1 == 2",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.EQUAL), make(Opcode.POP) ],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "1 != 2",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.NOT_EQUAL),
          make(Opcode.POP) ],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "true == false",
      "instructions": [
          make(Opcode.TRUE),
          make(Opcode.FALSE),
          make(Opcode.EQUAL),
          make(Opcode.POP) ],
      "constants": [] },
    { "expression": "true != false",
      "instructions": [
          make(Opcode.TRUE),
          make(Opcode.FALSE),
          make(Opcode.NOT_EQUAL),
          make(Opcode.POP) ],
      "constants": [] },
]


@pytest.mark.parametrize("test", COMPARISON_OPERATORS_TESTS)
def test_comparison_operators(test):
    _compile_and_assert(test)


PREFIX_EXPRESSIONS_TESTS = [
    { "expression": "-1",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.MINUS), make(Opcode.POP)],
      "constants": [Integer(1)] },
    { "expression": "!true",
      "instructions": [make(Opcode.TRUE), make(Opcode.BANG), make(Opcode.POP)],
      "constants": [] },
]


@pytest.mark.parametrize("test", PREFIX_EXPRESSIONS_TESTS)
def test_prefix_expressions(test):
    _compile_and_assert(test)


CONDITIONALS_TESTS = [
    { "expression": "if (true) { 10 }; 3333;",
      "instructions": [
          make(Opcode.TRUE),                    # 0
          make(Opcode.JUMP_NOT_TRUTHY, [10]),   # 1
          make(Opcode.CONSTANT, [0]),           # 4
          make(Opcode.JUMP, [11]),              # 7
          make(Opcode.NULL),                    # 10
          make(Opcode.POP),                     # 11
          make(Opcode.CONSTANT, [1]),           # 12
          make(Opcode.POP),                     # 15
        ],
      "constants": [
          Integer(10),
          Integer(3333)
      ] },
    { "expression": "if (true) { 10 };",
      "instructions": [
          make(Opcode.TRUE),                    # 0
          make(Opcode.JUMP_NOT_TRUTHY, [10]),   # 1
          make(Opcode.CONSTANT, [0]),           # 4
          make(Opcode.JUMP, [11]),              # 7
          make(Opcode.NULL),                    # 10
          make(Opcode.POP),                     # 11
        ],
      "constants": [
          Integer(10),
      ] },
]


@pytest.mark.parametrize("test", CONDITIONALS_TESTS)
def test_conditionals(test):
    _compile_and_assert(test)


GLOBAL_LET_STATEMENTS_TESTS = [
    { "expression": "let one = 1;",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.SET_GLOBAL, [0]),
      ],
      "constants": [
          Integer(1),
      ] },
    { "expression": "let one = 1; let two = 2;",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.SET_GLOBAL, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.SET_GLOBAL, [1]),
      ],
      "constants": [
          Integer(1),
          Integer(2),
      ] },
    { "expression": "let one = 1; one;",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.SET_GLOBAL, [0]),
          make(Opcode.GET_GLOBAL, [0]),
          make(Opcode.POP),
      ],
      "constants": [
          Integer(1),
      ] },
    { "expression": "let one = 1; let two = one; two;",
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.SET_GLOBAL, [0]),
          make(Opcode.GET_GLOBAL, [0]),
          make(Opcode.SET_GLOBAL, [1]),
          make(Opcode.GET_GLOBAL, [1]),
          make(Opcode.POP),
      ],
      "constants": [
          Integer(1),
      ] },
]


@pytest.mark.parametrize("test", GLOBAL_LET_STATEMENTS_TESTS)
def test_global_let_statements(test):
    _compile_and_assert(test)


STRING_EXPRESSION_TESTS = [
    { "expression": '"monkey"',
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.POP) ],
      "constants": [
          String("monkey") ] },
    { "expression": '"mon" + "key"',
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.ADD),
          make(Opcode.POP) ],
      "constants": [
          String("mon"),
          String("key") ] },
    { "expression": '"toad" > "worm"',
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.GREATER_THAN),
          make(Opcode.POP) ],
      "constants": [
          String("toad"),
          String("worm") ] },
    { "expression": '"moon" < "eggs"',
      "instructions": [
          make(Opcode.CONSTANT, [0]),
          make(Opcode.CONSTANT, [1]),
          make(Opcode.LESS_THAN),
          make(Opcode.POP) ],
      "constants": [
          String("moon"),
          String("eggs") ] },
]


@pytest.mark.parametrize("test", STRING_EXPRESSION_TESTS)
def test_string_expressions(test):
    _compile_and_assert(test)


ARRAY_LITERALS_TESTS = [
    {"expression": "[]",
     "instructions": [
         make(Opcode.ARRAY, [0]),
         make(Opcode.POP)],
     "constants": [ ] },
    {"expression": "[1, 2, 3]",
     "instructions": [
         make(Opcode.CONSTANT, [0]),
         make(Opcode.CONSTANT, [1]),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.ARRAY, [3]),
         make(Opcode.POP)],
     "constants": [
         Integer(1),
         Integer(2),
         Integer(3),
     ]},
    {"expression": "[1 + 2, 3 - 4, 5 * 6]",
     "instructions": [
         make(Opcode.CONSTANT, [0]),
         make(Opcode.CONSTANT, [1]),
         make(Opcode.ADD),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.CONSTANT, [3]),
         make(Opcode.SUBTRACT),
         make(Opcode.CONSTANT, [4]),
         make(Opcode.CONSTANT, [5]),
         make(Opcode.MULTIPLY),
         make(Opcode.ARRAY, [3]),
         make(Opcode.POP)],
     "constants": [
         Integer(1),
         Integer(2),
         Integer(3),
         Integer(4),
         Integer(5),
         Integer(6),
     ]},
]


@pytest.mark.parametrize("test", ARRAY_LITERALS_TESTS)
def test_array_literals(test):
    _compile_and_assert(test)


HASH_LITERALS_TESTS = [
    {"expression": "{}",
     "instructions": [
         make(Opcode.HASH, [0]),
         make(Opcode.POP)],
     "constants": [ ] },
    {"expression": "{1: 2, 3: 4, 5: 6}",
     "instructions": [
         make(Opcode.CONSTANT, [0]),
         make(Opcode.CONSTANT, [1]),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.CONSTANT, [3]),
         make(Opcode.CONSTANT, [4]),
         make(Opcode.CONSTANT, [5]),
         make(Opcode.HASH, [3]),
         make(Opcode.POP)],
     "constants": [
         Integer(1),
         Integer(2),
         Integer(3),
         Integer(4),
         Integer(5),
         Integer(6),
     ] },
    {"expression": "{1: 2 + 3, 4: 5 * 6}",
     "instructions": [
         make(Opcode.CONSTANT, [0]),
         make(Opcode.CONSTANT, [1]),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.ADD),
         make(Opcode.CONSTANT, [3]),
         make(Opcode.CONSTANT, [4]),
         make(Opcode.CONSTANT, [5]),
         make(Opcode.MULTIPLY),
         make(Opcode.HASH, [2]),
         make(Opcode.POP)],
     "constants": [
         Integer(1),
         Integer(2),
         Integer(3),
         Integer(4),
         Integer(5),
         Integer(6),
     ] },
]


@pytest.mark.parametrize("test", HASH_LITERALS_TESTS)
def test_hash_literals(test):
    _compile_and_assert(test)


INDEX_EXPRESSIONS_TESTS = [
    {"expression": "[1, 2, 3][1 + 1]",
     "instructions": [
         make(Opcode.CONSTANT, [0]),
         make(Opcode.CONSTANT, [1]),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.ARRAY, [3]),
         make(Opcode.CONSTANT, [3]),
         make(Opcode.CONSTANT, [4]),
         make(Opcode.ADD),
         make(Opcode.INDEX),
         make(Opcode.POP) ],
     "constants": [
         Integer(1),
         Integer(2),
         Integer(3),
         Integer(1),
         Integer(1) ]},
    {"expression": "{1: 2}[2 - 1]",
     "instructions": [
         make(Opcode.CONSTANT, [0]),
         make(Opcode.CONSTANT, [1]),
         make(Opcode.HASH, [1]),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.CONSTANT, [3]),
         make(Opcode.SUBTRACT),
         make(Opcode.INDEX),
         make(Opcode.POP) ],
     "constants": [
         Integer(1),
         Integer(2),
         Integer(2),
         Integer(1) ]},
]


@pytest.mark.parametrize("test", INDEX_EXPRESSIONS_TESTS)
def test_index_expressions(test):
    _compile_and_assert(test)


FUNCTIONS_TESTS = [
    {"expression": "fn() { return 5 + 10; }",
     "instructions": [
        make(Opcode.CLOSURE, [2, 0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(5),
         Integer(10),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.ADD),
            make(Opcode.RETURN_VALUE)]) ] },
    {"expression": "fn() { 5 + 10 }",
     "instructions": [
        make(Opcode.CLOSURE, [2, 0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(5),
         Integer(10),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.ADD),
            make(Opcode.RETURN_VALUE)]) ] },
    {"expression": "fn() { 1; 2 }",
     "instructions": [
        make(Opcode.CLOSURE, [2, 0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(1),
         Integer(2),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.POP),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.RETURN_VALUE)]) ] },
]


@pytest.mark.parametrize("test", FUNCTIONS_TESTS)
def test_functions(test):
    _compile_and_assert(test)


VOID_FUNCTIONS_TESTS = [
    {"expression": "fn() { }",
     "instructions": [
        make(Opcode.CLOSURE, [0, 0]),
        make(Opcode.POP) ],
     "constants": [
         CompiledFunction.from_instructions([
            make(Opcode.RETURN)])
         ] },
]

@pytest.mark.parametrize("test", VOID_FUNCTIONS_TESTS)
def test_void_functions(test):
    _compile_and_assert(test)


FUNCTION_CALLS_TESTS = [
    {"expression": "fn() { 24 }()",
     "instructions": [
        make(Opcode.CLOSURE, [1, 0]),
        make(Opcode.CALL, [0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(24),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.RETURN_VALUE)])
         ] },
    {"expression": "let noArg = fn() { 24 }; noArg();",
     "instructions": [
        make(Opcode.CLOSURE, [1, 0]),
        make(Opcode.SET_GLOBAL, [0]),
        make(Opcode.GET_GLOBAL, [0]),
        make(Opcode.CALL, [0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(24),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.RETURN_VALUE)])
         ] },
    {"expression": "let oneArg = fn(a) { }; oneArg(24);",
     "instructions": [
        make(Opcode.CLOSURE, [0, 0]),
        make(Opcode.SET_GLOBAL, [0]),
        make(Opcode.GET_GLOBAL, [0]),
        make(Opcode.CONSTANT, [1]),
        make(Opcode.CALL, [1]),
        make(Opcode.POP) ],
     "constants": [
         CompiledFunction.from_instructions([ make(Opcode.RETURN) ], 1, 1),
        Integer(24) ] },
    {"expression": "let manyArg = fn(a, b, c) { }; manyArg(24, 25, 26);",
     "instructions": [
        make(Opcode.CLOSURE, [0, 0]),
        make(Opcode.SET_GLOBAL, [0]),
        make(Opcode.GET_GLOBAL, [0]),
        make(Opcode.CONSTANT, [1]),
        make(Opcode.CONSTANT, [2]),
        make(Opcode.CONSTANT, [3]),
        make(Opcode.CALL, [3]),
        make(Opcode.POP) ],
     "constants": [
         CompiledFunction.from_instructions([ make(Opcode.RETURN) ], 3, 3),
        Integer(24), Integer(25), Integer(26) ] },
    {"expression": "let oneArg = fn(a) { a }; oneArg(24);",
     "instructions": [
        make(Opcode.CLOSURE, [0, 0]),
        make(Opcode.SET_GLOBAL, [0]),
        make(Opcode.GET_GLOBAL, [0]),
        make(Opcode.CONSTANT, [1]),
        make(Opcode.CALL, [1]),
        make(Opcode.POP) ],
     "constants": [
         CompiledFunction.from_instructions([ make(Opcode.GET_LOCAL, [0]), make(Opcode.RETURN_VALUE) ], 1, 1),
        Integer(24) ] },
    {"expression": "let manyArg = fn(a, b, c) { a; b; c }; manyArg(24, 25, 26);",
     "instructions": [
        make(Opcode.CLOSURE, [0, 0]),
        make(Opcode.SET_GLOBAL, [0]),
        make(Opcode.GET_GLOBAL, [0]),
        make(Opcode.CONSTANT, [1]),
        make(Opcode.CONSTANT, [2]),
        make(Opcode.CONSTANT, [3]),
        make(Opcode.CALL, [3]),
        make(Opcode.POP) ],
     "constants": [
        CompiledFunction.from_instructions([
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.POP),
            make(Opcode.GET_LOCAL, [1]),
            make(Opcode.POP),
            make(Opcode.GET_LOCAL, [2]),
            make(Opcode.RETURN_VALUE)
        ], 3, 3),
        Integer(24), Integer(25), Integer(26) ] },
]

@pytest.mark.parametrize("test", FUNCTION_CALLS_TESTS)
def test_function_calls(test):
    _compile_and_assert(test)


LET_STATEMENT_SCOPES_TESTS = [
    {"expression": "let num = 55; fn() { num }",
     "instructions": [
        make(Opcode.CONSTANT, [0]),
        make(Opcode.SET_GLOBAL, [0]),
        make(Opcode.CLOSURE, [1, 0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(55),
         CompiledFunction.from_instructions([
            make(Opcode.GET_GLOBAL, [0]),
            make(Opcode.RETURN_VALUE)])
         ] },
    {"expression": "fn() { let num = 55; num }",
     "instructions": [
        make(Opcode.CLOSURE, [1, 0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(55),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SET_LOCAL, [0]),
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.RETURN_VALUE)], 1)
         ] },
    {"expression": "fn() { let a = 55; let b = 77; a + b }",
     "instructions": [
        make(Opcode.CLOSURE, [2, 0]),
        make(Opcode.POP) ],
     "constants": [
         Integer(55),
         Integer(77),
         CompiledFunction.from_instructions([
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SET_LOCAL, [0]),
            make(Opcode.CONSTANT, [1]),
            make(Opcode.SET_LOCAL, [1]),
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.GET_LOCAL, [1]),
            make(Opcode.ADD),
            make(Opcode.RETURN_VALUE)], 2)
         ] },
]


@pytest.mark.parametrize("test", LET_STATEMENT_SCOPES_TESTS)
def test_let_statement_scopes(test):
    _compile_and_assert(test)


BUILTINS_TESTS = [
    {"expression": "len([]); push([], 3);",
     "instructions": [
        make(Opcode.GET_BUILTIN, [0]),
        make(Opcode.ARRAY, [0]),
        make(Opcode.CALL, [1]),
        make(Opcode.POP),
        make(Opcode.GET_BUILTIN, [4]),
        make(Opcode.ARRAY, [0]),
        make(Opcode.CONSTANT, [0]),
        make(Opcode.CALL, [2]),
        make(Opcode.POP) ],
     "constants": [
         Integer(3) ] },
    {"expression": "fn() { len([]) }",
     "instructions": [
        make(Opcode.CLOSURE, [0, 0]),
        make(Opcode.POP) ],
     "constants": [
         CompiledFunction.from_instructions([
            make(Opcode.GET_BUILTIN, [0]),
            make(Opcode.ARRAY, [0]),
            make(Opcode.CALL, [1]),
            make(Opcode.RETURN_VALUE)], 0, 0) ] },
]


@pytest.mark.parametrize("test", BUILTINS_TESTS)
def test_builtins(test):
    _compile_and_assert(test)


CLOSURES_TESTS = [
    {"expression": "fn(a) { fn(b) { a + b } }",
     "instructions": [
        make(Opcode.CLOSURE, [1, 0]),
        make(Opcode.POP) ],
     "constants": [
         CompiledFunction.from_instructions([
            make(Opcode.GET_FREE, [0]),
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.ADD),
            make(Opcode.RETURN_VALUE)], 1, 1),
         CompiledFunction.from_instructions([
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.CLOSURE, [0, 1]),
            make(Opcode.RETURN_VALUE)], 1, 1) ] }
]


@pytest.mark.parametrize("test", CLOSURES_TESTS)
def test_closures(test):
    _compile_and_assert(test)


RECURSIVE_FUNCTIONS_TESTS = [
    {"expression": "let countDown = fn(x) { countDown(x - 1); }; countDown(1);",
     "instructions": [
         make(Opcode.CLOSURE, [1, 0]),
         make(Opcode.SET_GLOBAL, [0]),
         make(Opcode.GET_GLOBAL, [0]),
         make(Opcode.CONSTANT, [2]),
         make(Opcode.CALL, [1]),
         make(Opcode.POP) ],
     "constants": [
         Integer(1),
         CompiledFunction.from_instructions([
            make(Opcode.CURRENT_CLOSURE),
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SUBTRACT),
            make(Opcode.CALL, [1]),
            make(Opcode.RETURN_VALUE) ], 1, 1),
        Integer(1) ] },
    {"expression": "let wrapper = fn() { let countDown = fn(x) { countDown(x - 1); }; countDown(1); }; wrapper();",
     "instructions": [
         make(Opcode.CLOSURE, [3, 0]),
         make(Opcode.SET_GLOBAL, [0]),
         make(Opcode.GET_GLOBAL, [0]),
         make(Opcode.CALL, [0]),
         make(Opcode.POP) ],
     "constants": [
         Integer(1),
         CompiledFunction.from_instructions([
            make(Opcode.CURRENT_CLOSURE),
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.CONSTANT, [0]),
            make(Opcode.SUBTRACT),
            make(Opcode.CALL, [1]),
            make(Opcode.RETURN_VALUE) ], 1, 1),
        Integer(1),
        CompiledFunction.from_instructions([
            make(Opcode.CLOSURE, [1, 0]),
            make(Opcode.SET_LOCAL, [0]),
            make(Opcode.GET_LOCAL, [0]),
            make(Opcode.CONSTANT, [2]),
            make(Opcode.CALL, [1]),
            make(Opcode.RETURN_VALUE) ], 1, 0) ] }
]


@pytest.mark.parametrize("test", RECURSIVE_FUNCTIONS_TESTS)
def test_recursive_functions(test):
    _compile_and_assert(test)
