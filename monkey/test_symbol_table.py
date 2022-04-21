# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from .compiler import SymbolTable, Symbol, SymbolScope


def test_define():
    global_table = SymbolTable()
    assert global_table.define("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert global_table.define("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert global_table.define("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert global_table.define("b") == Symbol("b", SymbolScope.GLOBAL, 1)


def test_resolve():
    global_table = SymbolTable()
    global_table.define("a")
    global_table.define("b")
    for symbol in [Symbol("a", SymbolScope.GLOBAL, 0), Symbol("b", SymbolScope.GLOBAL, 1)]:
        assert global_table.resolve(symbol.name) == symbol
    assert global_table.resolve("c") is None
