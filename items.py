from dataclasses import dataclass


@dataclass
class Item:
    name: str
    kind: str
    value: int = 0
