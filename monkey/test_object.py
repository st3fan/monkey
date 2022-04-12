# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.environment import Environment
from monkey.evaluator import Evaluator
from monkey.lexer import Lexer
from monkey.object import Object, Function
from monkey.parser import Parser


def eval(program: str) -> Object:
    environment = Environment()
    return Evaluator().eval(Parser(Lexer(program)).parse_program(),environment)
