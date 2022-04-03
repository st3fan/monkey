
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


def test_str_if_statement():
    assert str(parse("if (x < 3) { return true; }")) == "if (x < 3) { return true; }"
    assert str(parse("if (x < 3) { return true; } else { return false; }")) == "if (x < 3) { return true; } else { return false; }"

def test_str_if_expression():
    assert str(parse("let x = if (x < 3) { true };")) == "let x = if (x < 3) { true };"
    assert str(parse("let x = if (x < 3) { true } else { false };")) == "let x = if (x < 3) { true } else { false };"
