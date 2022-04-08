# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.evaluator import Evaluator, TRUE, FALSE, NULL
from monkey.lexer import Lexer
from monkey.object import Object, Integer, Boolean, Null
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
