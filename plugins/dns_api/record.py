from dataclasses import dataclass


@dataclass
class Record:
    domain: str
    name: str
    ttl: int
    type: str
    values: list