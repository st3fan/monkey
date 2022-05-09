# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import Optional

from .ast import Program
from .compiler import Bytecode, Compiler
from .environment import Environment
from .evaluator import Evaluator
from .lexer import Lexer
from .object import Object, Integer
from .parser import Parser
from .vm import VirtualMachine


RECURSIVE_FIBONACCI = """
    let fibonacci = fn(x) {
        if (x == 0) {
            return 0;
        } else {
            if (x == 1) {
                return 1;
            } else {
                fibonacci(x - 1) + fibonacci(x - 2);
            }
        }
    };
    fibonacci(16); fibonacci(16); fibonacci(16); fibonacci(16); fibonacci(16);
    fibonacci(16); fibonacci(16); fibonacci(16); fibonacci(16); fibonacci(16);
"""


def _compile_program(src: str) -> Bytecode:
    parser = Parser(Lexer(src))
    program = parser.parse_program()
    compiler = Compiler()
    compiler.compile(program)
    return compiler.bytecode()


def _parse_program(src: str) -> Program:
    return Parser(Lexer(src)).parse_program()


def test_interpret_recursive_fibonacci(benchmark):
    def recursive_fibonacci(bytecode: Bytecode):
        vm = VirtualMachine(bytecode)
        vm.run()
        return vm.last_popped_object()
    benchmark(recursive_fibonacci, _compile_program(RECURSIVE_FIBONACCI))


def test_evaluate_recursive_fibonacci(benchmark):
    def recursive_fibonacci(program):
        return Evaluator().eval(program, Environment())
    benchmark(recursive_fibonacci, _parse_program(RECURSIVE_FIBONACCI))
