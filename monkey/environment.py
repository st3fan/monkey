# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from dataclasses import dataclass, field
from typing import Dict, Optional

from monkey.object import Object


@dataclass
class Environment:
    store: Dict[str, Object] = field(default_factory=dict)

    def get(self, name: str) -> Optional[Object]:
        return self.store.get(name)
    
    def set(self, name: str, object: Object):
        self.store[name] = object
