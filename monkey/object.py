# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass
from enum import Enum


class ObjectType(Enum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"


class Object:
    def type(self) -> ObjectType:
        raise NotImplementedError()
    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class Integer(Object):
    value: int
    def type(self) -> ObjectType:
        return ObjectType.INTEGER
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool
    def type(self) -> ObjectType:
        return ObjectType.BOOLEAN
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Null(Object):
    def type(self) -> ObjectType:
        return ObjectType.NULL
    def __str__(self) -> str:
        return "null"
