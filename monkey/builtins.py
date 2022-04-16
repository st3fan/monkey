# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import List, Union

from .object import Array, Builtin, EvaluationError, Object, Integer, String, NULL, Boolean, Hash, Null


def builtin_len(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], String):
        return Integer(len(args[0].value))
    if isinstance(args[0], Array):
        return Integer(len(args[0].elements))
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


def builtin_puts(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], (String, Integer, Boolean)):
        print(args[0].value)
        return NULL
    return EvaluationError(f"argument to `puts` not supported, got {args[0].type()}")


def builtin_first(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        elements = args[0].elements
        return elements[0] if len(elements) else NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")
    

def builtin_last(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        elements = args[0].elements
        return elements[-1] if len(elements) else NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


def builtin_rest(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        elements = args[0].elements
        return Array(elements[1:]) if len(elements) else NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


BUILTINS: dict[str, Builtin] = {
    "len": Builtin(builtin_len),
    "puts": Builtin(builtin_puts),
    "first": Builtin(builtin_first),
    "last": Builtin(builtin_last),
    "rest": Builtin(builtin_rest),
}


# Lets see if we can make use of the type hints in the evaluator. Then we
# can drop the argument checks here and these builtins can just focus on
# their actual implementation.

def new_builtin_len(object: Union[String, Array, Hash]) -> Integer:
    match object:
        case String(value):
            return Integer(len(value))
        case Array(elements):
            return Integer(len(elements))
        case Hash(pairs):
            return Integer(len(pairs))


def new_builtin_first(array: Array) -> Object:
    if len(array.elements) != 0:
        return array.elements[0]
    return NULL


def new_builtin_last(array: Array) -> Object:
    if len(array.elements) != 0:
        return array.elements[-1]
    return NULL


def new_builtin_rest(array: Array) -> Union[Array, Null]:
    if len(array.elements) != 0:
        return Array(array.elements[1:])
    return NULL


NEW_BUILTINS: dict[str, Builtin] = {
    "len": Builtin(new_builtin_len),
    "first": Builtin(new_builtin_first),
    "last": Builtin(new_builtin_last),
    "rest": Builtin(new_builtin_rest),
}
