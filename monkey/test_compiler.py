# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import pytest

from .lexer import Lexer
from .parser import Parser
from .code import Opcode, make
from .compiler import Compiler, EmittedInstruction
from .object import Integer


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
    assert compiler.instructions == make(Opcode.CONSTANT, [0])


def test_last_prev_instruction():
    compiler = Compiler()
    assert compiler.prev_instruction is None
    assert compiler.last_instruction is None
    compiler.emit(Opcode.CONSTANT, [0])
    assert compiler.prev_instruction is None
    assert compiler.last_instruction == EmittedInstruction(Opcode.CONSTANT, 0)
    compiler.emit(Opcode.JUMP_NOT_TRUTHY, [0])
    assert compiler.prev_instruction == EmittedInstruction(Opcode.CONSTANT, 0)
    assert compiler.last_instruction == EmittedInstruction(Opcode.JUMP_NOT_TRUTHY, 3)
    compiler.emit(Opcode.JUMP, [0])
    assert compiler.prev_instruction == EmittedInstruction(Opcode.JUMP_NOT_TRUTHY, 3)
    assert compiler.last_instruction == EmittedInstruction(Opcode.JUMP, 6)


def test_change_operand():
    compiler = Compiler()
    compiler.emit(Opcode.JUMP, [0x1234])
    assert compiler.instructions[1] == 0x12
    assert compiler.instructions[2] == 0x34
    compiler.change_operand(0, 0x5678)
    assert compiler.instructions[1] == 0x56
    assert compiler.instructions[2] == 0x78


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



#
# Actual b'\x00\x00\x00 \x0f \x12\x00\x00' - Has a POP in between CONSTANT and SET_GLOBAL
# Expected b'\x00\x00\x00\x12\x00\x00'
#
# The only place where we insert a POP is in compile_expression_statement()
#


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

def test_disassemble():
    pass  # TODO
