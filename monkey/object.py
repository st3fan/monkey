# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List

from .ast import Identifier, BlockStatement
from .environment import Environment


class ObjectType(Enum):
    INTEGER = 0
    BOOLEAN = 1
    NULL = 2
    RETURN_VALUE = 3
    EVALUATION_ERROR = 4
    FUNCTION = 5
    STRING = 6
    BUILTIN = 7
    ARRAY = 8
    HASH = 9


@dataclass(frozen=True)
class Object:
    def type(self) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True)
class Integer(Object):
    value: int

    def type(self) -> str:
        return ObjectType.INTEGER.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Boolean(Object):
    value: bool

    def type(self) -> str:
        return ObjectType.BOOLEAN.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Null(Object):
    def type(self) -> str:
        return ObjectType.NULL.name

    def __str__(self) -> str:
        return "null"


@dataclass(frozen=True)
class ReturnValue(Object):
    value: Object

    def type(self) -> str:
        return ObjectType.RETURN_VALUE.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class EvaluationError(Object):
    message: str

    def type(self) -> str:
        return ObjectType.EVALUATION_ERROR.name

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class Function(Object):
    parameters: List[Identifier]
    body: BlockStatement
    environment: Environment

    def type(self) -> str:
        return ObjectType.FUNCTION.name

    def __str__(self) -> str:
        return str(self)  # TODO?


@dataclass(frozen=True)
class String(Object):
    value: str

    def type(self) -> str:
        return ObjectType.STRING.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Builtin(Object):
    value: Callable

    def type(self) -> str:
        return ObjectType.BUILTIN.name

    def __str__(self) -> str:
        return "builtin function"  # TODO Can we do something nicer here?


@dataclass(frozen=True)
class Array(Object):
    elements: List[Object]

    def type(self) -> str:
        return ObjectType.ARRAY.name

    def __str__(self) -> str:
        return "TODO"


@dataclass(frozen=True)
class Hash(Object):
    pairs: Dict[Object, Object] = field(default_factory=dict)

    def type(self) -> str:
        return ObjectType.HASH.name

    def __str__(self) -> str:
        return "TODO"


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)
