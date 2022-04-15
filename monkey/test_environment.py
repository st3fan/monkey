# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from monkey.environment import Environment
from monkey.object import Integer


def test_environment():
    e = Environment()
    e.set("foo", Integer(42))
    assert e.get("foo") == Integer(42)
    e.set("foo", Integer(7))
    assert e.get("foo") == Integer(7)


def test_outer_environment():
    outer = Environment()
    outer.set("outer", Integer(42))
    inner = Environment(outer=outer)
    assert outer.get("outer") == Integer(42)
    assert inner.get("outer") == Integer(42)
    assert inner.get("nope") is None
