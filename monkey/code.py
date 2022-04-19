# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from email.policy import default
from enum import IntEnum, unique
from struct import pack
from typing import Dict, List, Optional


#Instructions = NewType("Instructions", bytes)


@unique
class Opcode(IntEnum):
    CONSTANT = 0
    ADD = 1
    SUBTRACT = 2
    MULTIPLY = 3
    DIVIDE = 4
    TRUE = 5
    FALSE = 6
    GREATER_THAN = 7
    LESS_THAN = 8
    EQUAL = 9
    NOT_EQUAL = 10


@dataclass
class Definition:
    opcode: Opcode
    operand_widths: List[int] = field(default_factory=list)


DEFINITIONS: Dict[Opcode, Definition] = {
    Opcode.CONSTANT: Definition(Opcode.CONSTANT, [2]),
    Opcode.ADD: Definition(Opcode.ADD),
    Opcode.SUBTRACT: Definition(Opcode.SUBTRACT),
    Opcode.MULTIPLY: Definition(Opcode.MULTIPLY),
    Opcode.DIVIDE: Definition(Opcode.DIVIDE),
    Opcode.TRUE: Definition(Opcode.TRUE),
    Opcode.FALSE: Definition(Opcode.FALSE),
    Opcode.GREATER_THAN: Definition(Opcode.GREATER_THAN),
    Opcode.LESS_THAN: Definition(Opcode.LESS_THAN),
    Opcode.EQUAL: Definition(Opcode.EQUAL),
    Opcode.NOT_EQUAL: Definition(Opcode.NOT_EQUAL),
}


def lookup_definition(opcode: Opcode) -> Optional[Definition]:
    return DEFINITIONS.get(opcode) # Should it just raise because it is an internal error?


def make(opcode: Opcode, operands: List[int] = None) -> bytes:
    if (definition := lookup_definition(opcode)) is None:
        raise Exception(f"Cannot find definition for opcode {opcode}")

    if operands is None:
        operands = []

    if len(definition.operand_widths) != len(operands):
        raise Exception(f"Expected {len(definition.operand_widths)} operands but got {len(operands)}")

    instructions = bytes([opcode.value])
    for i, o in enumerate(operands):
        match definition.operand_widths[i]:
            case 2:
                instructions += pack(">H", o)

    return instructions
