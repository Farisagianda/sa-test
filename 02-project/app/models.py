import re
from pydantic import BaseModel, Field, field_validator, conint
from typing import List, Optional

DNS1123 = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$')

class EnvSpec(BaseModel):
    name: str
    team: str
    owner: str | None = None
    base_image: str
    packages: List[str] = []
    cpu: str = Field("500m")
    memory: str = Field("1Gi")
    gpu: Optional[conint(ge=0)] = 0
    pool: Optional[str] = None
    priority: Optional[str] = None

    @field_validator("name", "team")
    @classmethod
    def dns1123(cls, v: str) -> str:
        if not DNS1123.match(v.lower()):
            raise ValueError("must be DNS-1123 compatible")
        return v