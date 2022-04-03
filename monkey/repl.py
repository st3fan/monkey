

from monkey.lexer import Lexer
from monkey.token import Token, TokenType


def start():
    while True:
        s = input("> ")
        lexer = Lexer(s)
        while (token := lexer.next_token()) != Token(TokenType.EOF, ""):
            print(token)
