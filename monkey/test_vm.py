# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import Optional

import pytest

from .compiler import Compiler
from .lexer import Lexer
from .parser import Parser
from .object import Array, Hash, Object, Integer, Boolean, TRUE, FALSE, NULL, String
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
    ("!(if (false) { 5; })", True),
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


GLOBALS_TESTS = [
    ("let one = 1; one", Integer(1)),
    ("let one = 1; let two = 2; one + two", Integer(3)),
    ("let one = 1; let two = one + one; one + two", Integer(3)),
]


@pytest.mark.parametrize("expression, expected", GLOBALS_TESTS)
def test_globals(expression, expected):
    assert _interpret_expression(expression) == expected


STRING_EXPRESSIONS_TESTS = [
    ('"cow" > "bee"', TRUE),
    ('"cow" < "bee"', FALSE),
    ('"bee" > "cow"', FALSE),
    ('"bee" < "cow"', TRUE),
    ('"zebra" > "apple"', TRUE),
    ('"zebra" < "apple"', FALSE),
    ('"apple" > "zebra"', FALSE),
    ('"apple" < "zebra"', TRUE),
    ('"monkey"', String("monkey")),
    ('"mon"+"key"', String("monkey")),
]


@pytest.mark.parametrize("expression, expected", STRING_EXPRESSIONS_TESTS)
def test_string_expressions(expression, expected):
    assert _interpret_expression(expression) == expected


ARRAY_LITERALS_TESTS = [
    ("[]", Array([])),
    ("[1, 2, 3]", Array([Integer(1), Integer(2), Integer(3)])),
    ("[1 + 2, 3 * 4, 5 + 6]", Array([Integer(3), Integer(12), Integer(11)])),
]

@pytest.mark.parametrize("expression, expected", ARRAY_LITERALS_TESTS)
def test_array_literals(expression, expected):
    assert _interpret_expression(expression) == expected


HASH_LITERALS_TESTS = [
    ("{}", Hash()),
    ("{1: 2, 3: 4}", Hash(pairs={Integer(1): Integer(2), Integer(3): Integer(4)})),
    ("{1: 2 + 3, 4: 5 * 6}", Hash(pairs={Integer(1): Integer(5), Integer(4): Integer(30)})),
]

@pytest.mark.parametrize("expression, expected", HASH_LITERALS_TESTS)
def test_hash_literals(expression, expected):
    assert _interpret_expression(expression) == expected


INDEX_EXPRESSIONS_TESTS = [
    ("[1, 2, 3][1]", Integer(2)),
    ("[1, 2, 3][0 + 2]", Integer(3)),
    ("[[1, 1, 1]][0][0]", Integer(1)),
    ("[][0]", NULL),
    ("[1, 2, 3][99]", NULL),
    ("[1][-1]", NULL),
    ("{1: 1, 2: 2}[1]", Integer(1)),
    ("{1: 1, 2: 2}[2]", Integer(2)),
    ("{1: 1}[0]", NULL),
    ("{}[0]", NULL),
]


@pytest.mark.parametrize("expression, expected", INDEX_EXPRESSIONS_TESTS)
def test_index_expressions(expression, expected):
    assert _interpret_expression(expression) == expected


FUNCTION_CALLS_TESTS = [
    ("let fivePlusTen = fn() { 5 + 10; }; fivePlusTen();", Integer(15)),
    ("let one = fn() { 1; }; let two = fn() { 2; }; one() + two()", Integer(3)),
    ("let a = fn() { 1 }; let b = fn() { a() + 1 }; let c = fn() { b() + 1 }; c();", Integer(3)),
]


@pytest.mark.parametrize("expression, expected", FUNCTION_CALLS_TESTS)
def test_function_calls(expression, expected):
    assert _interpret_expression(expression) == expected


FUNCTION_CALLS_WITH_RETURN_TESTS = [
    ("let earlyExit = fn() { return 99; 100; }; earlyExit();", Integer(99)),
    ("let earlyExit = fn() { return 99; return 100; }; earlyExit();", Integer(99)),
]


@pytest.mark.parametrize("expression, expected", FUNCTION_CALLS_WITH_RETURN_TESTS)
def test_function_with_return_calls(expression, expected):
    assert _interpret_expression(expression) == expected


FUNCTION_CALLS_WITHOUT_RETURN_TESTS = [
    ("let noReturn = fn() { }; noReturn();", NULL),
    ("let noReturn = fn() { }; let noReturnTwo = fn() { noReturn(); }; noReturn(); noReturnTwo();", NULL),
]


@pytest.mark.parametrize("expression, expected", FUNCTION_CALLS_WITHOUT_RETURN_TESTS)
def test_function_without_return_calls(expression, expected):
    assert _interpret_expression(expression) == expected


VOID_FUNCTION_CALLS_TESTS = [
    # TODO
]


@pytest.mark.parametrize("expression, expected", VOID_FUNCTION_CALLS_TESTS)
def test_void_function_calls(expression, expected):
    assert _interpret_expression(expression) == expected


CALLING_FUNCTIONS_WITH_BINDINGS_TESTS = [
    ("let one = fn() { let one = 1; one }; one();", Integer(1)),
    ("let oneAndTwo = fn() { let one = 1; let two = 2; one + two; }; oneAndTwo();", Integer(3)),
    ("let oneAndTwo = fn() { let one = 1; let two = 2; one + two; }; let threeAndFour = fn() { let three = 3; let four = 4; three + four; }; oneAndTwo() + threeAndFour();", Integer(10)),
]


@pytest.mark.parametrize("expression, expected", CALLING_FUNCTIONS_WITH_BINDINGS_TESTS)
def test_calling_functions_with_bindings(expression, expected):
    assert _interpret_expression(expression) == expected


CALLING_FUNCTIONS_WITH_ARGUMENTS_AND_BINDINGS_TESTS = [
    ("let identity = fn(a) { a; }; identity(4);", Integer(4)),
    ("let sum = fn(a, b) { a + b; }; sum(1, 2);", Integer(3)),
    ("let sum = fn(a, b) { let c = a + b; c; }; sum(1, 2);", Integer(3)),
    ("let sum = fn(a, b) { let c = a + b; c; }; sum(1, 2) + sum(3, 4);", Integer(10)),
    ("let sum = fn(a, b) { let c = a + b; c; }; let outer = fn() { sum(1, 2) + sum(3, 4); }; outer();", Integer(10)),
    ("let globalNum = 10; let sum = fn(a, b) { let c = a + b; c + globalNum; }; let outer = fn() { sum(1, 2) + sum(3, 4) + globalNum; }; outer() + globalNum", Integer(50))
]


@pytest.mark.parametrize("expression, expected", CALLING_FUNCTIONS_WITH_ARGUMENTS_AND_BINDINGS_TESTS)
def test_calling_functions_with_arguments_and_bindings(expression, expected):
    assert _interpret_expression(expression) == expected


FIRST_CLASS_FUNCTIONS_TESTS = [
    ("let returnsThreeReturner = fn() { let returnsThree = fn() { 3; }; returnsThree; }; returnsThreeReturner()();", Integer(3)),
]


@pytest.mark.parametrize("expression, expected", FIRST_CLASS_FUNCTIONS_TESTS)
def test_first_class_functions(expression, expected):
    assert _interpret_expression(expression) == expected
