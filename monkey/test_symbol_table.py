# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from .compiler import SymbolTable, Symbol, SymbolScope


def test_define():
    global_table = SymbolTable()
    assert global_table.define("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert global_table.define("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    # TODO Should this behave like this?
    # assert global_table.define("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    # assert global_table.define("b") == Symbol("b", SymbolScope.GLOBAL, 1)


def test_resolve():
    global_table = SymbolTable()
    global_table.define("a")
    global_table.define("b")
    for symbol in [Symbol("a", SymbolScope.GLOBAL, 0), Symbol("b", SymbolScope.GLOBAL, 1)]:
        assert global_table.resolve(symbol.name) == symbol
    assert global_table.resolve("c") is None


def test_resolve_local():
    global_table = SymbolTable()
    global_table.define("a")
    global_table.define("b")

    local_table = SymbolTable(outer=global_table)
    local_table.define("c")
    local_table.define("d")

    assert global_table.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert global_table.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert global_table.resolve("c") == None
    assert global_table.resolve("d") == None

    assert local_table.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert local_table.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert local_table.resolve("c") == Symbol("c", SymbolScope.LOCAL, 0)
    assert local_table.resolve("d") == Symbol("d", SymbolScope.LOCAL, 1)


def test_resolve_nested_local():
    global_table = SymbolTable()
    global_table.define("a")
    global_table.define("b")

    local_table1 = SymbolTable(outer=global_table)
    local_table1.define("c")
    local_table1.define("d")

    local_table2 = SymbolTable(outer=local_table1)
    local_table2.define("e")
    local_table2.define("f")

    assert global_table.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert global_table.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert global_table.resolve("c") == None
    assert global_table.resolve("d") == None
    assert global_table.resolve("e") == None
    assert global_table.resolve("f") == None

    assert local_table1.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert local_table1.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert local_table1.resolve("c") == Symbol("c", SymbolScope.LOCAL, 0)
    assert local_table1.resolve("d") == Symbol("d", SymbolScope.LOCAL, 1)
    assert local_table1.resolve("e") == None
    assert local_table1.resolve("f") == None

    assert local_table2.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert local_table2.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert local_table2.resolve("c") == Symbol("c", SymbolScope.FREE, 0)
    assert local_table2.resolve("d") == Symbol("d", SymbolScope.FREE, 1)
    assert local_table2.resolve("e") == Symbol("e", SymbolScope.LOCAL, 0)
    assert local_table2.resolve("f") == Symbol("f", SymbolScope.LOCAL, 1)


def test_define_resolve_builtins():
    global_table = SymbolTable()
    first_local_table = SymbolTable(outer=global_table)
    second_local_table = SymbolTable(outer=first_local_table)

    for symbol_index, symbol_name in enumerate(["a", "b", "c", "d"]):
        global_table.define_builtin(symbol_index, symbol_name)

    for table in (global_table, first_local_table, second_local_table):
        for symbol_index, symbol_name in enumerate(["a", "b", "c", "d"]):
            assert table.resolve(symbol_name) == Symbol(symbol_name, SymbolScope.BUILTIN, symbol_index)


def test_resolve_free():
    global_table = SymbolTable()
    global_table.define("a")
    global_table.define("b")

    foo_table = SymbolTable(outer=global_table)
    foo_table.define("c")
    foo_table.define("d")

    bar_table = SymbolTable(outer=foo_table)
    bar_table.define("e")
    bar_table.define("f")

    assert foo_table.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert foo_table.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert foo_table.resolve("c") == Symbol("c", SymbolScope.LOCAL, 0)
    assert foo_table.resolve("d") == Symbol("d", SymbolScope.LOCAL, 1)
    assert foo_table.free_symbols == []

    assert bar_table.resolve("a") == Symbol("a", SymbolScope.GLOBAL, 0)
    assert bar_table.resolve("b") == Symbol("b", SymbolScope.GLOBAL, 1)
    assert bar_table.resolve("c") == Symbol("c", SymbolScope.FREE, 0)
    assert bar_table.resolve("d") == Symbol("d", SymbolScope.FREE, 1)
    assert bar_table.resolve("e") == Symbol("e", SymbolScope.LOCAL, 0)
    assert bar_table.resolve("f") == Symbol("f", SymbolScope.LOCAL, 1)
    assert bar_table.free_symbols == [Symbol("c", SymbolScope.LOCAL, 0), Symbol("d", SymbolScope.LOCAL, 1)]


def test_resolve_unresolvable_free():
    global_table = SymbolTable()
    global_table.define("a")

    foo_table = SymbolTable(outer=global_table)
    foo_table.define("c")

    bar_table = SymbolTable(outer=foo_table)
    bar_table.define("e")
    bar_table.define("f")

    expected = [
        Symbol("a", SymbolScope.GLOBAL, 0),
        Symbol("c", SymbolScope.FREE, 0),
        Symbol("e", SymbolScope.LOCAL, 0),
        Symbol("f", SymbolScope.LOCAL, 1),
    ]

    for symbol in expected:
        found = bar_table.resolve(symbol.name)
        assert found == symbol

    expected_unresolvable = ["b", "d"]

    for name in expected_unresolvable:
        assert bar_table.resolve(name) is None
