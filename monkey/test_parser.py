# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.ast import BooleanLiteral, ExpressionStatement, Identifier, InfixExpression, LetStatement, IntegerLiteral, PrefixExpression
from monkey.lexer import Lexer
from monkey.token import Token, TokenType
from monkey.parser import Parser


def parse_program(s):
    return Parser(Lexer(s)).parse_program()


def test_next_token():
    parser = Parser(Lexer("let x = 42;"))
    assert parser.current_token == Token(TokenType.LET, "let")
    parser.next_token()
    assert parser.current_token == Token(TokenType.IDENT, "x")
    parser.next_token()
    assert parser.current_token == Token(TokenType.ASSIGN, "=")
    parser.next_token()
    assert parser.current_token == Token(TokenType.INT, "42")
    parser.next_token()
    assert parser.current_token == Token(TokenType.SEMICOLON, ";")
    parser.next_token()
    assert parser.current_token == Token(TokenType.EOF, "")
    parser.next_token()
    assert parser.current_token == Token(TokenType.EOF, "")


def test_parse_let_statements():
    program = parse_program("let x = 5; let y = 10; let z = 838383;")
    assert len(program.statements) == 3
    assert isinstance(program.statements[0], LetStatement)
    assert program.statements[0].name == Identifier("x")
    assert isinstance(program.statements[1], LetStatement)
    assert program.statements[1].name == Identifier("y")
    assert isinstance(program.statements[2], LetStatement)
    assert program.statements[2].name == Identifier("z")


def test_parse_return_statements():
    program = parse_program("return 5; return 10; return 20;")
    assert len(program.statements) == 3


def test_identifier_expression():
    program = parse_program("foo;")
    assert len(program.statements) == 1
    assert isinstance(program.statements[0], ExpressionStatement)
    assert isinstance(program.statements[0].expression, Identifier)
    assert program.statements[0].expression.value == "foo"


def test_integer_expression():
    program = parse_program("42;")
    assert len(program.statements) == 1
    assert isinstance(program.statements[0], ExpressionStatement)
    assert isinstance(program.statements[0].expression, IntegerLiteral)
    assert program.statements[0].expression.value == 42


def test_prefix_expressions():
    program = parse_program("-42;")
    assert len(program.statements) == 1
    assert isinstance(program.statements[0], ExpressionStatement)
    assert isinstance(program.statements[0].expression, PrefixExpression)
    assert program.statements[0].expression.operator == "-"
    assert isinstance(program.statements[0].expression.right, IntegerLiteral)
    program = parse_program("!42;")
    assert len(program.statements) == 1
    assert isinstance(program.statements[0], ExpressionStatement)
    assert isinstance(program.statements[0].expression, PrefixExpression)
    assert program.statements[0].expression.operator == "!"
    assert isinstance(program.statements[0].expression.right, IntegerLiteral)
    program = parse_program("!foo;")
    assert len(program.statements) == 1
    assert isinstance(program.statements[0], ExpressionStatement)
    assert isinstance(program.statements[0].expression, PrefixExpression)
    assert program.statements[0].expression.operator == "!"
    assert isinstance(program.statements[0].expression.right, Identifier)


def test_boolean_prefix_expressions():
    for e in [("!", "true"), ("!", "false")]:
        program = parse_program(f"{e[0]}{e[1]}")
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], ExpressionStatement)
        assert isinstance(program.statements[0].expression, PrefixExpression)
        assert program.statements[0].expression.operator == e[0]
        assert isinstance(program.statements[0].expression.right, BooleanLiteral)
        assert program.statements[0].expression.right.value == (e[1] == "true")


def test_integer_infix_expressions():
    for operator in ("+", "-", "*", "/", ">", "<", "==", "!="):
        program = parse_program(f"5{operator}7")
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], ExpressionStatement)
        assert isinstance(program.statements[0].expression, InfixExpression)
        assert isinstance(program.statements[0].expression.left, IntegerLiteral)
        assert program.statements[0].expression.left.value == 5
        assert program.statements[0].expression.operator == operator
        assert isinstance(program.statements[0].expression.right, IntegerLiteral)
        assert program.statements[0].expression.right.value == 7


def test_boolean_infix_expressions():
    for e in [("true", "==", "true"), ("true", "!=", "false"), ("false", "==", "false")]:
        program = parse_program(f"{e[0]} {e[1]} {e[2]}")
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], ExpressionStatement)
        assert isinstance(program.statements[0].expression, InfixExpression)
        assert isinstance(program.statements[0].expression.left, BooleanLiteral)
        assert program.statements[0].expression.left.value == (e[0] == "true")
        assert program.statements[0].expression.operator == e[1]
        assert isinstance(program.statements[0].expression.right, BooleanLiteral)
        assert program.statements[0].expression.right.value == (e[2] == "true")


def test_operator_precedence():
    tests = [
        ("-a * b", "((-a) * b)",),
        ("!-a", "(!(-a))",),
        ("a + b + c", "((a + b) + c)",),
        ("a + b - c", "((a + b) - c)",),
        ("a * b * c", "((a * b) * c)",),
        ("a * b / c", "((a * b) / c)",),
        ("a + b / c", "(a + (b / c))",),
        ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)",),
        ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)",),
        ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))",),
        ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))",),
        ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",),
        ("true", "true"),
        ("false", "false"),
        ("3 > 5 == false", "((3 > 5) == false)"),
        ("3 < 5 == true", "((3 < 5) == true)"),
        ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
        ("(5 + 5) * 2", "((5 + 5) * 2)"),
        ("2 / (5 + 5)", "(2 / (5 + 5))"),
        ("-(5 + 5)", "(-(5 + 5))"),
        ("!(true == true)", "(!(true == true))"),
    ]
    for test in tests:
        assert str(parse_program(test[0])) == test[1]


def test_boolean_literals():
    expressions = [
        "true",
        "false",
        "let foobar = true;",
        "let barfoo = false;",
    ]
    for expression in expressions:
        assert str(parse_program(expression)) == expression


def test_function_literals():
    expressions = [
        "fn () { return true; }",
        "fn (x) { return x + 1; }",
        "fn (x, y) { return x + y; }",
    ]
    for expression in expressions:
        program = parse_program(expression)
        assert len(program.statements) == 1


def test_if_expressions():
    expressions = [
        "if (x < y) { x }",
        "if (x < y) { x } else { y }"
    ]
    for expression in expressions:
        assert str(parse_program(expression)) == expression


def test_if_statements():
    expressions = [
        "if (x < y) { return x; }",
        "if (x < y) { return x; } else { return y; }"
    ]
    for expression in expressions:
        assert str(parse_program(expression)) == expression


def test_block_statements():
    pass # TODO


def test_string_literals():
    expressions = [
        '""',
        '"a"',
        '"aa"'
    ]
    for expression in expressions:
        assert str(parse_program(expression)) == expression


def test_array_literals():
    expressions = [
        "[]",
        "[1]",
        "[1, 2, 3]",
        #"[1, [10], [[100], [200]]]"
    ]
    for expression in expressions:
        assert str(parse_program(expression)) == expression


def test_index_expression():
    expressions = [
        ("array[1]", "(array[1])"),
        ("array[a + b]", "(array[(a + b)])"),
        ("array[array[0]]", "(array[(array[0])])"),
    ]
    for expression in expressions:
        assert str(parse_program(expression[0])) == expression[1]


def test_index_expression_operator_precedence():
    expressions = [
        ("a * [1, 2, 3, 4][b * c] * d", "((a * ([1, 2, 3, 4][(b * c)])) * d)"),
        ("add(a * b[2], b[1], 2 * [1, 2][1])", "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))")
    ]
    for expression in expressions:
        assert str(parse_program(expression[0])) == expression[1]


def test_hash_literals():
    expressions = [
        ('{}', '{}'),
        ('{"foo": "bar"}', '{"foo":"bar"}'),
        ('{42: "bar"}', '{42:"bar"}'),
        ('{"foo": 42}', '{"foo":42}'),
        ('{key: value}', '{key:value}'),
        ('{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}', '{"one":(0 + 1), "two":(10 - 8), "three":(15 / 5)}')
    ]
    for expression in expressions:
        assert str(parse_program(expression[0])) == expression[1]
