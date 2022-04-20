# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import Optional

import pytest

from .compiler import Compiler
from .lexer import Lexer
from .parser import Parser
from .object import Object, Integer, Boolean, TRUE, FALSE, NULL
from .vm import VirtualMachine


def _interpret_expression(expression) -> Optional[Object]:
    parser = Parser(Lexer(expression))
    program = parser.parse_program()
    compiler = Compiler()
    compiler.compile(program)
    vm = VirtualMachine(compiler.bytecode())
    vm.run()
    return vm.last_popped_object()


INTEGER_ARITHMETIC_TESTS = [
    ("0", 0),
    ("5", 5),
    ("5+7", 12),
    ("5-7", -2),
    ("5*7", 35),
    ("15/5", 3),
    ("1 - 2", -1),
    ("1 * 2", 2),
    ("4 / 2", 2),
    ("50 / 2 * 2 + 10 - 5", 55),
    ("5 + 5 + 5 + 5 - 10", 10),
    ("2 * 2 * 2 * 2 * 2", 32),
    ("5 * 2 + 10", 20),
    ("5 + 2 * 10", 25),
    ("5 * (2 + 10)", 60),
    ("-5", -5),
    ("-10", -10),
    ("-50 + 100 + -50", 0),
    ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
]


@pytest.mark.parametrize("expression, expected", INTEGER_ARITHMETIC_TESTS)
def test_integer_arithmetic(expression, expected):
    assert _interpret_expression(expression) == Integer(expected)


def test_booleans():
    assert _interpret_expression("true") == TRUE
    assert _interpret_expression("false") == FALSE


BOOLEAN_EXPRESSIONS_TEST = [
    ("1 < 2", True),
    ("1 > 2", False),
    ("1 < 1", False),
    ("1 > 1", False),
    ("1 == 1", True),
    ("1 != 1", False),
    ("1 == 2", False),
    ("1 != 2", True),
    ("true == true", True),
    ("false == false", True),
    ("true == false", False),
    ("true != false", True),
    ("false != true", True),
    ("(1 < 2) == true", True),
    ("(1 < 2) == false", False),
    ("(1 > 2) == true", False),
    ("(1 > 2) == false", True),
    ("(1 < 2) != true", False),
    ("(1 < 2) != false", True),
    ("(1 > 2) != true", True),
    ("(1 > 2) != false", False),
    ("!true", False),
    ("!false", True),
    ("!5", False),
    ("!!true", True),
    ("!!false", False),
    ("!!5", True),
    ("!(if (false) { 5; })", True)
]


@pytest.mark.parametrize("expression, expected", BOOLEAN_EXPRESSIONS_TEST)
def test_boolean_expressions(expression, expected):
    assert _interpret_expression(expression) == Boolean(expected)


CONDITIONALS_TESTS = [
    ("if (1 > 2) { 10 }", NULL),
    ("if (false) { 10 }", NULL),
    ("if (true) { 10 }", Integer(10)),
    ("if (true) { 10 } else { 20 }", Integer(10)),
    ("if (false) { 10 } else { 20 } ", Integer(20)),
    ("if (1) { 10 }", Integer(10)),
    ("if (1 < 2) { 10 }", Integer(10)),
    ("if (1 < 2) { 10 } else { 20 }", Integer(10)),
    ("if (1 > 2) { 10 } else { 20 }", Integer(20)),
    ("if ((if (false) { 10 })) { 10 } else { 20 }", Integer(20)),
]


@pytest.mark.parametrize("expression, expected", CONDITIONALS_TESTS)
def test_conditionals(expression, expected):
    assert _interpret_expression(expression) == expected
