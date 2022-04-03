from monkey.lexer import Lexer
from monkey.token import Token, TokenType


def test_read_identifier():
    lexer = Lexer("hello")
    assert lexer.read_identifier() == "hello"


def test_next_token():
    input = "=+(){},;"
    expected_tokens = [
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.PLUS, "+"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.SEMICOLON, ";")
    ]
    lexer = Lexer(input)
    for expected_token in expected_tokens:
        token = lexer.next_token()
        assert token == expected_token


def test_equal():
    input = "foo == bar"
    expected_tokens = [
        Token(TokenType.IDENT, "foo"),
        Token(TokenType.EQ, "=="),
        Token(TokenType.IDENT, "bar"),
    ]
    lexer = Lexer(input)
    for expected_token in expected_tokens:
        token = lexer.next_token()
        assert token == expected_token

def test_not_equal():
    input = "foo != bar"
    expected_tokens = [
        Token(TokenType.IDENT, "foo"),
        Token(TokenType.NOT_EQ, "!="),
        Token(TokenType.IDENT, "bar"),
    ]
    lexer = Lexer(input)
    for expected_token in expected_tokens:
        token = lexer.next_token()
        assert token == expected_token


def test_keywords():
    input = "if (5 < 10) {\nreturn true;\n} else {\nreturn false;\n}"
    expected_tokens = [
        Token(TokenType.IF, "if"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.INT, "5"),
        Token(TokenType.LT, "<"),
        Token(TokenType.INT, "10"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RETURN, "return"),
        Token(TokenType.TRUE, "true"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.ELSE, "else"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RETURN, "return"),
        Token(TokenType.FALSE, "false"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
    ]
    lexer = Lexer(input)
    for expected_token in expected_tokens:
        token = lexer.next_token()
        assert token == expected_token


def test_next_token_complex():
    input = "let five = 5;\nlet ten = 10;\nlet add = fn(x, y) {\n  x + y;\n};\nlet result = add(five, ten);\n!-/*5;\n5 < 10 > 5;\n"
    expected_tokens = [
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "five"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.INT, "5"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "ten"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.INT, "10"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "add"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.FUNCTION, "fn"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.IDENT, "x"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENT, "y"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.IDENT, "x"),
        Token(TokenType.PLUS, "+"),
        Token(TokenType.IDENT, "y"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "result"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.IDENT, "add"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.IDENT, "five"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENT, "ten"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.SEMICOLON, ";"),

        Token(TokenType.BANG, "!"),
        Token(TokenType.MINUS, "-"),
        Token(TokenType.SLASH, "/"),
        Token(TokenType.ASTERISK, "*"),
        Token(TokenType.INT, "5"),
        Token(TokenType.SEMICOLON, ";"),

        Token(TokenType.INT, "5"),
        Token(TokenType.LT, "<"),
        Token(TokenType.INT, "10"),
        Token(TokenType.GT, ">"),
        Token(TokenType.INT, "5"),

        Token(TokenType.SEMICOLON, ";"),

        Token(TokenType.EOF, ""),
    ]
    lexer = Lexer(input)
    for expected_token in expected_tokens:
        token = lexer.next_token()
        assert token == expected_token
