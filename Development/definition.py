class Percept:
    def __init__(self, name, pos):
        self.name = name      # "breeze", "stench", "glitter", etc.
        self.pos = pos        # (x, y)

class Literal:
    def __init__(self, name, pos, negate=False):
        self.name = name
        self.pos = pos
        self.negate = negate
    
    def __str__(self):
        return f"{'¬' if self.negate else ''}{self.name}{self.pos}"
    
    def __repr__(self):
        return f"Literal('{self.name}', {self.pos}, {self.negate})"
    
    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return (self.name == other.name and 
                self.pos == other.pos and 
                self.negate == other.negate)
    
    def __hash__(self):
        return hash((self.name, self.pos, self.negate))