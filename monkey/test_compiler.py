# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import pytest

from .lexer import Lexer
from .parser import Parser
from .code import Opcode, make
from .compiler import Compiler
from .object import Integer


def _compile_and_assert(test):
    program = Parser(Lexer(test["expression"])).parse_program()
    compiler = Compiler()
    compiler.compile(program)
    bytecode = compiler.bytecode()
    assert bytecode.instructions == b''.join(test["instructions"])
    assert bytecode.constants == test["constants"]


INTEGER_ARITHMETIC_TESTS = [
    { "expression": "7 + 5",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.ADD)],
      "constants": [Integer(7), Integer(5)] },
    { "expression": "7 - 5",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.SUBTRACT)],
      "constants": [Integer(7), Integer(5)] },
    { "expression": "7 * 5",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.MULTIPLY)],
      "constants": [Integer(7), Integer(5)] },
    { "expression": "7 * 5",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.MULTIPLY)],
      "constants": [Integer(7), Integer(5)] },
]


@pytest.mark.parametrize("test", INTEGER_ARITHMETIC_TESTS)
def test_integer_arithmetic(test):
    _compile_and_assert(test)


BOOLEAN_TESTS = [
    { "expression": "true",
      "instructions": [make(Opcode.TRUE)],
      "constants": [] },
    { "expression": "false",
      "instructions": [make(Opcode.FALSE)],
      "constants": [] },
]


@pytest.mark.parametrize("test", BOOLEAN_TESTS)
def test_booleans_arithmetic(test):
    _compile_and_assert(test)


COMPARISON_OPERATORS_TESTS = [
    { "expression": "1 > 2",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.GREATER_THAN)],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "1 < 2",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.LESS_THAN)],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "1 == 2",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.EQUAL)],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "1 != 2",
      "instructions": [make(Opcode.CONSTANT, [0]), make(Opcode.CONSTANT, [1]), make(Opcode.NOT_EQUAL)],
      "constants": [Integer(1), Integer(2)] },
    { "expression": "true == false",
      "instructions": [make(Opcode.TRUE), make(Opcode.FALSE), make(Opcode.EQUAL)],
      "constants": [] },
    { "expression": "true != false",
      "instructions": [make(Opcode.TRUE), make(Opcode.FALSE), make(Opcode.NOT_EQUAL)],
      "constants": [] },
]


@pytest.mark.parametrize("test", COMPARISON_OPERATORS_TESTS)
def test_comparison_operators(test):
    _compile_and_assert(test)


def test_disassemble():
    pass  # TODO
