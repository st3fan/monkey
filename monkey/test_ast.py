
from monkey.lexer import Lexer
from monkey.parser import Parser


def parse(s):
    return Parser(Lexer(s)).parse_program()


def test_str_let():
    assert str(parse("let foo = bar;")) == "let foo = bar;"
    assert str(parse("let foo = 42;")) == "let foo = 42;"
    assert str(parse("let   foo\t =\n 42 ;")) == "let foo = 42;"


def test_str_return():
    assert str(parse("return 42;")) == "return 42;"
    assert str(parse("return foo;")) == "return foo;"
