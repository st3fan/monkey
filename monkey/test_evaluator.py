# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.evaluator import Evaluator, TRUE, FALSE, NULL
from monkey.lexer import Lexer
from monkey.object import Object, Integer, Boolean, Null, EvaluationError
from monkey.parser import Parser


def eval(program: str) -> Object:
    return Evaluator().eval(Parser(Lexer(program)).parse_program())


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


def test_infix_error_handling():
    assert eval("5 + true") == EvaluationError("type mismatch: INTEGER + BOOLEAN")
    assert eval("5 + true; 5") == EvaluationError("type mismatch: INTEGER + BOOLEAN")
    assert eval("true + false") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval("true + false; 5;") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval("if (10 > 1) { true + false; }") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
    assert eval("if (10 > 1) { if (10 > 1) { return true + false; } return 1; }") == EvaluationError("unknown operator: BOOLEAN + BOOLEAN")
