# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from .environment import Environment
from .evaluator import Evaluator, NULL
from .lexer import Lexer
from .object import Object, Integer, EvaluationError, Array, String, Builtin
from .parser import Parser


def test_builtin_typing():
    def hello(name: String, age: Integer) -> Object:
        return String(f"Hello, {name}. I see you are {age} years old.")
    builtin = Builtin("hello", hello)
    assert builtin.argument_types == [String, Integer]

def _eval(program: str, expected_object: Object):
    environment = Environment()
    evaluated = Evaluator().eval(Parser(Lexer(program)).parse_program(),environment)
    assert evaluated == expected_object


def test_len():
    _eval('len("")', Integer(0))
    _eval('len("bacon")', Integer(5))
    _eval('len()', EvaluationError("wrong number of arguments. got=0, want=1"))
    _eval('len("a", "b")', EvaluationError("wrong number of arguments. got=2, want=1"))
    _eval('len(1)', EvaluationError("argument to `len` not supported, got INTEGER"))
    _eval('len([])', Integer(0))
    _eval('len([1])', Integer(1))
    _eval('len([1,2])', Integer(2))


def test_puts(capsys):
    _eval('puts("Hello, world!")', NULL)
    assert capsys.readouterr().out == "Hello, world!\n"


def test_first():
    _eval('first([])', NULL)
    _eval('first([3,5,7])', Integer(3))
    _eval('first([3])', Integer(3))


def test_last():
    # _eval('last([])', NULL)
    _eval('last([3,5,7])', Integer(7))
    _eval('last([3])', Integer(3))


def test_rest():
    _eval('rest([1,2,3])', Array([Integer(2), Integer(3)]))
    _eval('rest([2,3])', Array([Integer(3)]))
    _eval('rest([3])', Array([]))
    _eval('rest([])', NULL)
