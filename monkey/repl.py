

from monkey.lexer import Lexer
from monkey.parser import Parser
from monkey.token import Token, TokenType


def start():
    while True:
        s = input("> ")
        program = Parser(Lexer(s)).parse_program()
        print(str(program))
