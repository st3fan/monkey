# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Environment:
    outer: Any = field(default=None)  # TODO How do we use Object here instead?
    store: Dict[str, Any] = field(default_factory=dict)  # TODO Should be private/internal

    def get(self, name: str) -> Optional[Any]:
        if value := self.store.get(name):
            return value
        if self.outer:
            return self.outer.get(name)
        return None
    
    def set(self, name: str, value: Any) -> Any:
        self.store[name] = value
        return value
