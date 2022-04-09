# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# TODO Used to import Object but that results in a circular dependency (Function.environment)

@dataclass
class Environment:
    outer: Any = field(default=None) # TODO How do we do this?
    store: Dict[str, Any] = field(default_factory=dict) # TODO Should be private/internal

    def get(self, name: str) -> Optional[Any]:
        if object := self.store.get(name):
            return object
        if self.outer:
            return self.outer.get(name)
        return None
    
    def set(self, name: str, object: Any) -> Any:
        self.store[name] = object
        return object
