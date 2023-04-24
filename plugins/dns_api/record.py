from dataclasses import dataclass


@dataclass
class Record:
    name: str
    ttl: int
    type: str
    values: list