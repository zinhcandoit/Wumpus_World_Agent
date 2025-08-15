from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Literal:
    name: str
    pos: Tuple[int, int]
    negate: bool = False
    at_step: int = 0 # Used to reset knowledge when wumpus change (Shoot / Wumpus Move)
    
    def __repr__(self):
        return f"{'¬' if self.negate else ''}{self.name}{self.pos}"
    
    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return (self.name == other.name and 
                self.pos == other.pos and 
                self.negate == other.negate
                and self.at_step == self.at_step)
    
    def __hash__(self):
        return hash((self.name, self.pos, self.negate))