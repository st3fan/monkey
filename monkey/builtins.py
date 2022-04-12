# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import List

from monkey.object import Builtin, EvaluationError, Object, Null, Integer, String, NULL


# TODO Fun thing to do here could be to have a decorator to type check the arguments
# like @arguments(String) and then we can generate the errors dynamically. Also
# destructure the arguments instead of having args: List[Object].


def Len(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], String):
        return Integer(len(args[0].value)) # TODO Do all the checks
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


def Puts(args: List[Object]) -> Object:
    if len(args) != 1:
        return EvaluationError(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], String):
        print(args[0].value)
        return NULL
    return EvaluationError(f"argument to `len` not supported, got {args[0].type()}")


BUILTINS: dict[str, Builtin] = {
    "len": Builtin(Len),
    "puts": Builtin(Puts)
}
