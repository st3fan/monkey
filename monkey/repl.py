# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.compiler import Compiler, CompilerState
from monkey.lexer import Lexer
from monkey.parser import Parser
from monkey.vm import VirtualMachine, VirtualMachineState


def start():
    compiler_state = CompilerState()
    virtual_machine_state = VirtualMachineState()

    while True:
        s = input("> ")
        program = Parser(Lexer(s)).parse_program()

        compiler = Compiler(compiler_state)
        compiler.compile(program)

        virtual_machine = VirtualMachine(compiler.bytecode(), virtual_machine_state)
        virtual_machine.run()

        if result := virtual_machine.last_popped_object():
            print(result)
