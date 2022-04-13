# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import List

from monkey.object import Array, Builtin, EvaluationError, Object, Null, Integer, String, NULL


def Len(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], String):
        return Integer(len(args[0].value))
    if isinstance(args[0], Array):
        return Integer(len(args[0].elements))
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


def Puts(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], String):
        print(args[0].value)
        return NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


def First(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        elements = args[0].elements
        return elements[0] if len(elements) else NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")
    


def Last(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        elements = args[0].elements
        return elements[-1] if len(elements) else NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


def Rest(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        elements = args[0].elements
        return Array(elements[1:]) if len(elements) else NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


BUILTINS: dict[str, Builtin] = {
    "len": Builtin(Len),
    "puts": Builtin(Puts),
    "first": Builtin(First),
    "last": Builtin(Last),
    "rest": Builtin(Rest),
}
