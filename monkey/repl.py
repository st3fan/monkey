# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.environment import Environment
from monkey.evaluator import Evaluator
from monkey.lexer import Lexer
from monkey.parser import Parser


def start():
    environment = Environment()
    while True:
        s = input("> ")
        program = Parser(Lexer(s)).parse_program()
        # TODO Check for parse errors and report
        if evaluated := Evaluator().eval(program, environment):
            print(evaluated)
