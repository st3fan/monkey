# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import List, Union

from .object import Array, Builtin, Object, Integer, String, NULL, Boolean, Hash, Null


def builtin_len(object: Union[String, Array, Hash]) -> Integer:
    match object:
        case String(value):
            return Integer(len(value))
        case Array(elements):
            return Integer(len(elements))
        case Hash(pairs):
            return Integer(len(pairs))


def builtin_first(array: Array) -> Object:
    if len(array.elements) != 0:
        return array.elements[0]
    return NULL


def builtin_last(array: Array) -> Object:
    if len(array.elements) != 0:
        return array.elements[-1]
    return NULL


def builtin_rest(array: Array) -> Union[Array, Null]:
    if len(array.elements) != 0:
        return Array(array.elements[1:])
    return NULL


def builtin_push(array: Array, value: Object) -> Object:
    new_array = Array(array.elements.copy() + [value])
    return new_array


def builtin_puts(o: Union[String, Integer, Boolean]) -> Object:
    match o:
        case Integer(value):
            print(value)
        case String(value):
            print(value)
        case Boolean(value):
            print("true" if value else "false")
    return NULL


BUILTINS: list[Builtin] = [
    Builtin("len", builtin_len),
    Builtin("first", builtin_first),
    Builtin("last", builtin_last),
    Builtin("rest", builtin_rest),
    Builtin("push", builtin_push),
    Builtin("puts", builtin_puts),
]


BUILTINS_BY_NAME: dict[str, Builtin] = {builtin.name: builtin for builtin in BUILTINS}
