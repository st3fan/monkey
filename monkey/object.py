# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from enum import Enum
from inspect import getfullargspec
from typing import Any, Callable, Dict, List, TypeVar
from typing_extensions import Self

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
    COMPILED_FUNCTION = 10


@dataclass(frozen=True)
class Object:
    @classmethod
    def type(cls) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True)
class Integer(Object):
    value: int

    @classmethod
    def type(cls) -> str:
        return ObjectType.INTEGER.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Boolean(Object):
    value: bool

    @classmethod
    def type(cls) -> str:
        return ObjectType.BOOLEAN.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Null(Object):
    @classmethod
    def type(cls) -> str:
        return ObjectType.NULL.name

    def __str__(self) -> str:
        return "null"


@dataclass(frozen=True)
class ReturnValue(Object):
    value: Object

    @classmethod
    def type(cls) -> str:
        return ObjectType.RETURN_VALUE.name

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class EvaluationError(Object):
    message: str

    @classmethod
    def type(cls) -> str:
        return ObjectType.EVALUATION_ERROR.name

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class Function(Object):
    parameters: List[Identifier]
    body: BlockStatement
    environment: Environment

    @classmethod
    def type(cls) -> str:
        return ObjectType.FUNCTION.name

    def __str__(self) -> str:
        return str(self)  # TODO?


@dataclass(frozen=True)
class CompiledFunction(Object):
    instructions: bytes
    num_locals: int
    num_parameters: int

    @classmethod
    def from_instructions(cls, instructions: List[bytes], num_locals: int = 0, num_parameters: int = 0) -> "CompiledFunction": # TODO Python 3.11 has Self
        return cls(b''.join(instructions), num_locals, num_parameters)

    @classmethod
    def type(cls) -> str:
        return ObjectType.COMPILED_FUNCTION.name

    def __str__(self) -> str:
        return "TODO"


@dataclass(frozen=True)
class String(Object):
    value: str

    @classmethod
    def type(cls) -> str:
        return ObjectType.STRING.name

    def __str__(self) -> str:
        return "TODO"


@dataclass(frozen=True)
class Builtin(Object):
    name: str
    callable: Callable

    argument_types: List[Any] = field(init = False, compare=False)
    return_type: Any = field(init = False, compare=False)

    def __post_init__(self):
        super().__init__()
        args_spec = getfullargspec(self.callable)
        object.__setattr__(self, "argument_types", [args_spec.annotations[arg] for arg in args_spec.args])
        object.__setattr__(self, "return_type", args_spec.annotations.get('return', Null))

    @classmethod
    def type(cls) -> str:
        return ObjectType.BUILTIN.name

    def __str__(self) -> str:
        return f"builtin {self.callable.__name__}({''.join(self.argument_types)}) -> {self.return_type}"


@dataclass(frozen=True)
class Array(Object):
    elements: List[Object]

    @classmethod
    def type(cls) -> str:
        return ObjectType.ARRAY.name

    def __str__(self) -> str:
        return "TODO"


@dataclass(frozen=True)
class Hash(Object):
    pairs: Dict[Object, Object] = field(default_factory=dict)

    @classmethod
    def type(cls) -> str:
        return ObjectType.HASH.name

    def __str__(self) -> str:
        return "TODO"


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)
