# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.environment import Environment
from monkey.evaluator import Evaluator, TRUE, FALSE, NULL
from monkey.lexer import Lexer
from monkey.object import Object, Integer, Null, EvaluationError, Function, String
from monkey.parser import Parser


def eval(program: str) -> Object:
    environment = Environment()
    return Evaluator().eval(Parser(Lexer(program)).parse_program(),environment)


def test_eval_integer_expression():
    assert eval("-7") == Integer(-7)
    assert eval("-5") == Integer(-5)
    assert eval("0") == Integer(0)
    assert eval("5") == Integer(5)
    assert eval("7") == Integer(7)
    assert eval("5 + 5 + 5 + 5 - 10") == Integer(10)
    assert eval("2 * 2 * 2 * 2 * 2") == Integer(32)
    assert eval("-50 + 100 + -50") == Integer(0)
    assert eval("5 * 2 + 10") == Integer(20)
    assert eval("5 + 2 * 10") == Integer(25)
    assert eval("20 + 2 * -10") == Integer(0)
    assert eval("50 / 2 * 2 + 10") == Integer(60)
    assert eval("2 * (5 + 10)") == Integer(30)
    assert eval("3 * 3 * 3 + 10") == Integer(37)
    assert eval("3 * (3 * 3) + 10") == Integer(37)
    assert eval("(5 + 10 * 2 + 15 / 3) * 2 + -10") == Integer(50)


def test_eval_boolean_expression():
    assert eval("true") is TRUE
    assert eval("false") is FALSE
    assert eval("1 < 2") is TRUE
    assert eval("1 > 2") is FALSE
    assert eval("1 < 1") is FALSE
    assert eval("1 > 1") is FALSE
    assert eval("1 == 1") is TRUE
    assert eval("1 != 1") is FALSE
    assert eval("1 == 2") is FALSE
    assert eval("1 != 2") is TRUE
    assert eval("3 == true") is FALSE
    assert eval("false != 3") is TRUE


def test_eval_null():
    assert eval("") == Null()
    assert eval("") is NULL


def test_bang_operator():
    assert eval("!true") is FALSE
    assert eval("!false") is TRUE
    assert eval("!!true") is TRUE
    assert eval("!!false") is FALSE
    assert eval("!0") is TRUE
    assert eval("!1") is FALSE
    assert eval("!3") is FALSE


def test_if_else_expressions():
    assert eval("if (true) { 10 }") == Integer(10)
    assert eval("if (false) { 10 }") == NULL
    assert eval("if (1) { 10 }") == Integer(10)
    assert eval("if (1 < 2) { 10 }") == Integer(10)
    assert eval("if (1 > 2) { 10 }") == NULL
    assert eval("if (1 > 2) { 10 } else { 20 }") == Integer(20)
    assert eval("if (1 < 2) { 10 } else { 20 }") == Integer(10)


def test_return_statements():
    assert eval("return 10;") == Integer(10)
    assert eval("return 10; 9;") == Integer(10)
    assert eval("return 2 * 5; 9;") == Integer(10)
    assert eval("9; return 2 * 5; 9;") == Integer(10)
    assert eval("if (10 > 1) { if (10 > 1) { return 10; } return 1; }") == Integer(10)


def test_prefix_error_handling():
    assert eval("-true") == EvaluationError("unknown operator: -BOOLEAN")
    assert eval("-true; 5;") == EvaluationError("unknown operator: -BOOLEAN")
    assert eval("return -true;") == EvaluationError("unknown operator: -BOOLEAN")
    assert eval("if (10 > 1) { return -true; }") == EvaluationError("unknown operator: -BOOLEAN")
    assert eval('-"egg"') == EvaluationError("unknown operator: -STRING")
    assert eval('!"ham"') == EvaluationError("unknown operator: !STRING")
    assert eval('if (10 > 1) { return -"eh"; }') == EvaluationError("unknown operator: -STRING")


def test_infix_error_handling():
    assert eval("5 + true") == EvaluationError("type mismatch: INTEGER + BOOLEAN")
    assert eval("5 + true; 5") == EvaluationError("type mismatch: INTEGER + BOOLEAN")
    assert eval("true + false") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval("true + false; 5;") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval("if (10 > 1) { true + false; }") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval("if (10 > 1) { if (10 > 1) { return true + false; } return 1; }") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval('"hi" + true') == EvaluationError("type mismatch: STRING + BOOLEAN")
    assert eval('"hi" + 1234') == EvaluationError("type mismatch: STRING + INTEGER")
    assert eval('true + "hi"') == EvaluationError("type mismatch: BOOLEAN + STRING")
    assert eval('1234 + "hi"') == EvaluationError("type mismatch: INTEGER + STRING")
    assert eval('"oh" - "hi"') == EvaluationError("unknown operator: STRING - STRING")
    assert eval('"oh" / "hi"') == EvaluationError("unknown operator: STRING / STRING")
    assert eval('"oh" * "hi"') == EvaluationError("unknown operator: STRING * STRING")


def test_let_statement():
    assert eval("let a = 5; a;") == Integer(5)
    assert eval("let a = 5 * 5; a;") == Integer(25)
    assert eval("let a = 5; let b = a; b;") == Integer(5)
    assert eval("let a = 5; let b = a; let c = a + b + 5; c;") == Integer(15)


def test_identifier_error_handling():
    assert eval("nope") == EvaluationError("identifier not found: nope")


def test_function_object():
    function_object = eval("fn(x) { x + 2; };")
    assert isinstance(function_object, Function)
    # TODO Test all Function properties


def test_eval_function():
    assert eval("let identity = fn(x) { x; }; identity(5);") == Integer(5)
    assert eval("let identity = fn(x) { return x; }; identity(5);") == Integer(5)
    assert eval("let double = fn(x) { x * 2; }; double(5);") == Integer(10)
    assert eval("let add = fn(x, y) { x + y; }; add(5, 5);") == Integer(10)
    assert eval("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));") == Integer(20)
    assert eval('let hello = fn(name) { "Hello, " + name + "!"; }; hello("Kramer");') == String("Hello, Kramer!")
    assert eval("fn(x) { x; }(5)") == Integer(5)
    assert eval('fn(x) { x; }("wow")') == String("wow")


def test_closures():
    assert eval("let newAdder = fn(x) { fn(y) { x + y }; }; let addTwo = newAdder(2); addTwo(2);") == Integer(4)
    assert eval("let v = 21; let foo = fn(x) { v*x }; foo(2);")  == Integer(42)


def test_eval_string_literals():
    assert eval('""') == String("")
    assert eval('"a"') == String("a")
    assert eval('"aa"') == String("aa")


def test_eval_string_expressions():
    assert eval('"peanut" + "butter"') == String("peanutbutter")
    assert eval('"foo" + "bar" + "baz"') == String("foobarbaz")
    assert eval('"" + "cheese"') == String("cheese")
    assert eval('"cheese" + ""') == String("cheese")
    assert eval('"a" == "b"') == FALSE
    assert eval('"b" == "b"') == TRUE
    assert eval('"a" != "b"') == TRUE
    assert eval('"a" != "a"') == FALSE
    assert eval('"a" < "b"') == TRUE
    assert eval('"b" < "a"') == FALSE
    assert eval('"a" > "b"') == FALSE
    assert eval('"b" > "a"') == TRUE
