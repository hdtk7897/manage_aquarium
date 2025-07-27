from typing import Optional
import strawberry

from schema import aquaenvType
from resolver import get_aquaenv_by_id, get_aquaenv_list

@strawberry.type
class Query:
    aeuaenvs: list[aquaenvType] = strawberry.field(resolver=get_aquaenv_list)
    aquaenv: Optional[aquaenvType] = strawberry.field(resolver=get_aquaenv_by_id)