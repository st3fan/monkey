# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass
from enum import Enum
from typing import List

from monkey.ast import Identifier, BlockStatement
from monkey.environment import Environment


class ObjectType(Enum):
    INTEGER = 0
    BOOLEAN = 1
    NULL = 2
    RETURN_VALUE = 3
    EVALUATION_ERROR = 4
    FUNCTION = 5


@dataclass
class Object:
    def type(self) -> str:
        raise NotImplementedError()
    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class Integer(Object):
    value: int
    def type(self) -> str:
        return ObjectType.INTEGER.name
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool
    def type(self) -> str:
        return ObjectType.BOOLEAN.name
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Null(Object):
    def type(self) -> str:
        return ObjectType.NULL.name
    def __str__(self) -> str:
        return "null"


@dataclass
class ReturnValue(Object):
    value: Object
    def type(self) -> str:
        return ObjectType.RETURN_VALUE.name
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class EvaluationError(Object):
    message: str
    def type(self) -> str:
        return ObjectType.EVALUATION_ERROR.name
    def __str__(self) -> str:
        return self.message


@dataclass
class Function(Object):
    parameters: List[Identifier]
    body: BlockStatement
    environment: Environment
    def type(self) -> str:
        return ObjectType.FUNCTION.name
    def __str__(self) -> str:
        return str(self) # TODO?
