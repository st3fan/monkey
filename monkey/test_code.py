# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import struct

import pytest

from .code import Opcode, make


def test_make_constants():
    assert make(Opcode.CONSTANT, [0]) == bytes([0, 0, 0])
    assert make(Opcode.CONSTANT, [65534]) == bytes([0, 255, 254])


def test_make_booleans():
    assert make(Opcode.TRUE) == bytes([5])
    assert make(Opcode.FALSE) == bytes([6])


def test_make_checks():
    with pytest.raises(Exception, match="Expected 1 operands but got 0"):
        make(Opcode.CONSTANT, [])
    with pytest.raises(Exception, match="Expected 1 operands but got 2"):
        make(Opcode.CONSTANT, [1, 2])
    with pytest.raises(Exception, match="Cannot find definition for opcode 1234567890"):
        make(1234567890, [])


def test_make_overflow():
    with pytest.raises(struct.error, match="'H' format requires 0 <= number <= 65535"):
        make(Opcode.CONSTANT, [65536])
    with pytest.raises(struct.error, match="argument out of range"):
        make(Opcode.CONSTANT, [-1])


def test_make_get_set_local():
    assert make(Opcode.SET_LOCAL, [42]) == bytes([Opcode.SET_LOCAL, 42])
    assert make(Opcode.GET_LOCAL, [42]) == bytes([Opcode.GET_LOCAL, 42])