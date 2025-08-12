from Development.definition import Literal
import random
from Development.algorithm import get_possible_actions, classify_all_literals, make_clause
class Agent:
    def __init__(self, num_wumpus=2, map_size=None):
        self.start_location = (map_size - 1, 0)
        self.location = (map_size - 1, 0)
        self.wumpus_remain = num_wumpus
        self.direction = 'E'
        self.has_gold = False
        self.has_arrow = True
        self.size_known = map_size  # Initially known size of the map 
        self.visited = set()
        self.percepts = [] # New percepts at current location
        self.KB = set()  # Agent won't know the size of the map until getting bump
    
    def update_direction(self, action):
        directions = ['N', 'E', 'S', 'W']
        current_index = directions.index(self.direction)
        if action == 'turn left':
                new_index = (current_index - 1) % 4 
        else:
                new_index = (current_index + 1) % 4
        self.direction = directions[new_index]

    
    def get_KB_from_percepts(self):
        """Extract KB from percepts. size_known may be None (unknown)."""
        look_around = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        current_pos = self.location

        def in_bounds(pos):
            if self.size_known is None:
                return True
            y, x = pos
            return 0 <= y < self.size_known and 0 <= x < self.size_known
        
        valid_current = in_bounds(current_pos)
        if valid_current:
            self.visited.add(current_pos)

        percept_names = {p.name for p in self.percepts}

        # negative inferences: only when current pos valid (and in_bounds uses size_known logic)
        if valid_current and "stench" not in percept_names:
            for dy, dx in look_around:
                nb = (current_pos[0] + dy, current_pos[1] + dx)
                if in_bounds(nb):
                    c = make_clause([Literal("wumpus", nb, True)])
                    if c:
                        self.KB.add(c)
            self.KB.add(make_clause([Literal("stench", tuple(current_pos), True)]))

        if valid_current and "breeze" not in percept_names:
            for dy, dx in look_around:
                nb = (current_pos[0] + dy, current_pos[1] + dx)
                if in_bounds(nb):
                    c = make_clause([Literal("pit", nb, True)])
                    if c:
                        self.KB.add(c)
            self.KB.add(make_clause([Literal("breeze", tuple(current_pos), True)]))
        # process each percept (use tuple(percept.pos) when creating Literals)
        for percept in self.percepts:
            ppos = tuple(percept.pos)

            if percept.name == 'glitter':
                c = make_clause([Literal("gold", ppos, False)])
                if c:
                    self.KB.add(c)

            if percept.name == 'stench':
                or_literals = []
                for dy, dx in look_around:
                    nb = (ppos[0] + dy, ppos[1] + dx)
                    if in_bounds(nb):
                        or_literals.append(Literal("wumpus", nb, False))
                        impl = make_clause([Literal("wumpus", nb, True), Literal("stench", ppos, False)])
                        if impl:
                            self.KB.add(impl)
                # add the stench literal itself
                or_literals.append(Literal("stench", ppos, True))
                c = make_clause(or_literals)
                if c:
                    self.KB.add(c)
                self.KB.add(make_clause([Literal("stench", ppos, False)]))
                self.KB.add(make_clause([Literal("wumpus", ppos, True), Literal("pit", ppos, True)]))

            if percept.name == 'breeze':
                or_literals = []
                for dy, dx in look_around:
                    nb = (ppos[0] + dy, ppos[1] + dx)
                    if in_bounds(nb):
                        or_literals.append(Literal("pit", nb, False))
                        impl = make_clause([Literal("pit", nb, True), Literal("breeze", ppos, False)])
                        if impl:
                            self.KB.add(impl)
                or_literals.append(Literal("breeze", ppos, True))
                c = make_clause(or_literals)
                if c:
                    self.KB.add(c)
                self.KB.add(make_clause([Literal("breeze", ppos, False)]))
                self.KB.add(make_clause([Literal("wumpus", ppos, True), Literal("pit", ppos, True)]))

            if percept.name == 'bump':
                # deduce map size from bump percept position
                new_size = max(ppos[0], ppos[1]) + 1
                # update only if smaller or if size_known was None => set it
                if (self.size_known is None) or (new_size < self.size_known):
                    self.size_known = new_size
                    # prune self.KB to remove clauses referencing out-of-bounds cells
                    new_KB = set()
                    for clause in self.KB:
                        keep = True
                        for lit in clause:
                            if not in_bounds(lit.pos):
                                keep = False
                                break
                        if keep:
                            new_KB.add(clause)
                    self.KB = new_KB

            if percept.name == 'scream':
                pass
                #self.KB.add(make_clause([Literal('wumpus', percept.pos, True)]))
                '''direction_moves = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
                dy, dx = direction_moves[self.direction]
                i = 1
                literal = []
                while True:
                    nb = (self.location[0] + i * dy, self.location[1] + i * dx)
                    if not in_bounds(nb):
                        break
                    # Sửa: Cook lại cái literal thành: con trước mặt, đã biết cook
                    literal.append(Literal("wumpus", nb, True)) #Vế siu mạnh
                    c = make_clause(literal)
                    if c:
                        self.KB.add(c)
                    i += 1'''

        # Constraint: Pit and Wumpus cannot be in the same cell (¬Pit ∨ ¬Wumpus)
        if valid_current:
            for dy, dx in look_around:
                pos = (current_pos[0] + dy, current_pos[1] + dx)
                if in_bounds(pos):
                    c = make_clause([Literal("pit", pos, True), Literal("wumpus", pos, True)])
                    if c:
                        self.KB.add(c)

        # clear percepts
        self.percepts = []
        
    def choose_action(self, mode='random'):
        if mode == 'random':
            result = classify_all_literals(self.KB) 
            for (name, pos), status in sorted(result.items()):
                pos_str = f"({', '.join(map(str, pos))})" if pos else ""
                print(f"{name}{pos_str}: {status}")
            get_action = get_possible_actions(self, result)
            print("Possible actions:", get_action)
            if 'grab' in get_action:
                return 'grab'
            if 'move' in get_action and random.random() <= 0.7:
                return 'move'
            if 'climb out' in get_action and self.has_gold:
                return 'climb out'
            if 'shoot' in get_action and self.has_arrow:
                return 'shoot'
            return get_action.pop(random.randint(0, len(get_action) - 1))

