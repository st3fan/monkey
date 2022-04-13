# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.environment import Environment
from monkey.evaluator import Evaluator, TRUE, FALSE, NULL
from monkey.lexer import Lexer
from monkey.object import Object, Integer, Null, EvaluationError, Function, String
from monkey.parser import Parser


def _eval(program: str) -> Object:
    return Evaluator().eval(Parser(Lexer(program)).parse_program(), Environment())


def test_eval_integer_expression():
    assert _eval("-7") == Integer(-7)
    assert _eval("-5") == Integer(-5)
    assert _eval("0") == Integer(0)
    assert _eval("5") == Integer(5)
    assert _eval("7") == Integer(7)
    assert _eval("5 + 5 + 5 + 5 - 10") == Integer(10)
    assert _eval("2 * 2 * 2 * 2 * 2") == Integer(32)
    assert _eval("-50 + 100 + -50") == Integer(0)
    assert _eval("5 * 2 + 10") == Integer(20)
    assert _eval("5 + 2 * 10") == Integer(25)
    assert _eval("20 + 2 * -10") == Integer(0)
    assert _eval("50 / 2 * 2 + 10") == Integer(60)
    assert _eval("2 * (5 + 10)") == Integer(30)
    assert _eval("3 * 3 * 3 + 10") == Integer(37)
    assert _eval("3 * (3 * 3) + 10") == Integer(37)
    assert _eval("(5 + 10 * 2 + 15 / 3) * 2 + -10") == Integer(50)


def test_eval_boolean_expression():
    assert _eval("true") is TRUE
    assert _eval("false") is FALSE
    assert _eval("1 < 2") is TRUE
    assert _eval("1 > 2") is FALSE
    assert _eval("1 < 1") is FALSE
    assert _eval("1 > 1") is FALSE
    assert _eval("1 == 1") is TRUE
    assert _eval("1 != 1") is FALSE
    assert _eval("1 == 2") is FALSE
    assert _eval("1 != 2") is TRUE
    assert _eval("3 == true") is FALSE
    assert _eval("false != 3") is TRUE


def test_eval_null():
    assert _eval("") == Null()
    assert _eval("") is NULL


def test_bang_operator():
    assert _eval("!true") is FALSE
    assert _eval("!false") is TRUE
    assert _eval("!!true") is TRUE
    assert _eval("!!false") is FALSE
    assert _eval("!0") is TRUE
    assert _eval("!1") is FALSE
    assert _eval("!3") is FALSE


def test_if_else_expressions():
    assert _eval("if (true) { 10 }") == Integer(10)
    assert _eval("if (false) { 10 }") == NULL
    assert _eval("if (1) { 10 }") == Integer(10)
    assert _eval("if (1 < 2) { 10 }") == Integer(10)
    assert _eval("if (1 > 2) { 10 }") == NULL
    assert _eval("if (1 > 2) { 10 } else { 20 }") == Integer(20)
    assert _eval("if (1 < 2) { 10 } else { 20 }") == Integer(10)


def test_return_statements():
    assert _eval("return 10;") == Integer(10)
    assert _eval("return 10; 9;") == Integer(10)
    assert _eval("return 2 * 5; 9;") == Integer(10)
    assert _eval("9; return 2 * 5; 9;") == Integer(10)
    assert _eval("if (10 > 1) { if (10 > 1) { return 10; } return 1; }") == Integer(10)


def test_prefix_error_handling():
    assert _eval("-true") == EvaluationError("unknown operator: -BOOLEAN")
    assert _eval("-true; 5;") == EvaluationError("unknown operator: -BOOLEAN")
    assert _eval("return -true;") == EvaluationError("unknown operator: -BOOLEAN")
    assert _eval("if (10 > 1) { return -true; }") == EvaluationError("unknown operator: -BOOLEAN")
    assert _eval('-"egg"') == EvaluationError("unknown operator: -STRING")
    assert _eval('!"ham"') == EvaluationError("unknown operator: !STRING")
    assert _eval('if (10 > 1) { return -"eh"; }') == EvaluationError("unknown operator: -STRING")


def test_infix_error_handling():
    assert _eval("5 + true") == EvaluationError("type mismatch: INTEGER + BOOLEAN")
    assert _eval("5 + true; 5") == EvaluationError("type mismatch: INTEGER + BOOLEAN")
    assert _eval("true + false") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert _eval("true + false; 5;") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert _eval("if (10 > 1) { true + false; }") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert _eval("if (10 > 1) { if (10 > 1) { return true + false; } return 1; }") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert _eval('"hi" + true') == EvaluationError("type mismatch: STRING + BOOLEAN")
    assert _eval('"hi" + 1234') == EvaluationError("type mismatch: STRING + INTEGER")
    assert _eval('true + "hi"') == EvaluationError("type mismatch: BOOLEAN + STRING")
    assert _eval('1234 + "hi"') == EvaluationError("type mismatch: INTEGER + STRING")
    assert _eval('"oh" - "hi"') == EvaluationError("unknown operator: STRING - STRING")
    assert _eval('"oh" / "hi"') == EvaluationError("unknown operator: STRING / STRING")
    assert _eval('"oh" * "hi"') == EvaluationError("unknown operator: STRING * STRING")


def test_let_statement():
    assert _eval("let a = 5; a;") == Integer(5)
    assert _eval("let a = 5 * 5; a;") == Integer(25)
    assert _eval("let a = 5; let b = a; b;") == Integer(5)
    assert _eval("let a = 5; let b = a; let c = a + b + 5; c;") == Integer(15)


def test_identifier_error_handling():
    assert _eval("nope") == EvaluationError("identifier not found: nope")


def test_function_object():
    function_object = _eval("fn(x) { x + 2; };")
    assert isinstance(function_object, Function)
    # TODO Test all Function properties


def test_eval_function():
    assert _eval("let identity = fn(x) { x; }; identity(5);") == Integer(5)
    assert _eval("let identity = fn(x) { return x; }; identity(5);") == Integer(5)
    assert _eval("let double = fn(x) { x * 2; }; double(5);") == Integer(10)
    assert _eval("let add = fn(x, y) { x + y; }; add(5, 5);") == Integer(10)
    assert _eval("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));") == Integer(20)
    assert _eval('let hello = fn(name) { "Hello, " + name + "!"; }; hello("Kramer");') == String("Hello, Kramer!")
    assert _eval("fn(x) { x; }(5)") == Integer(5)
    assert _eval('fn(x) { x; }("wow")') == String("wow")


def test_closures():
    assert _eval("let newAdder = fn(x) { fn(y) { x + y }; }; let addTwo = newAdder(2); addTwo(2);") == Integer(4)
    assert _eval("let v = 21; let foo = fn(x) { v*x }; foo(2);")  == Integer(42)


def test_eval_string_literals():
    assert _eval('""') == String("")
    assert _eval('"a"') == String("a")
    assert _eval('"aa"') == String("aa")


def test_eval_string_expressions():
    assert _eval('"peanut" + "butter"') == String("peanutbutter")
    assert _eval('"foo" + "bar" + "baz"') == String("foobarbaz")
    assert _eval('"" + "cheese"') == String("cheese")
    assert _eval('"cheese" + ""') == String("cheese")
    assert _eval('"a" == "b"') == FALSE
    assert _eval('"b" == "b"') == TRUE
    assert _eval('"a" != "b"') == TRUE
    assert _eval('"a" != "a"') == FALSE
    assert _eval('"a" < "b"') == TRUE
    assert _eval('"b" < "a"') == FALSE
    assert _eval('"a" > "b"') == FALSE
    assert _eval('"b" > "a"') == TRUE


def test_eval_array_index_expressions():
    assert _eval("[1, 2, 3][0]") == Integer(1)
    assert _eval("[1, 2, 3][1]") == Integer(2)
    assert _eval("[1, 2, 3][2]") == Integer(3)
    assert _eval("let i = 0; [1][i];") == Integer(1)
    assert _eval("[1, 2, 3][1 + 1];") == Integer(3)
    assert _eval("let myArray = [1, 2, 3]; myArray[2];") == Integer(3)
    assert _eval("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];") == Integer(6)
    assert _eval("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]") == Integer(2)
    assert _eval("[1, 2, 3][3]") == NULL
    assert _eval("[1, 2, 3][-1]") == NULL
