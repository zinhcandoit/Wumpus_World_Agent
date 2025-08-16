from Development.definition import Literal
from Design.ImageManager.Image import Image
from Development.algorithm import *
from constant import *
import random
class Agent:
    def __init__(self, num_wumpus=2, map_size=None):
        self.start_location = (map_size - 1, 0)
        self.location = (map_size - 1, 0)
        self.wumpus_remain = num_wumpus
        self.actions = []
        self.direction = 'E'
        self.has_gold = False
        self.has_arrow = True
        self.wumpus_die = None
        self.size_known = map_size
        self.visited = set()
        self.percepts = [] # New percepts at current location
        self.KB = set()

        self.agent_image = Image('assets/agent.png', 50, 50, 0, 0)
    
    def update_direction(self, action):
        directions = ['N', 'E', 'S', 'W']
        current_index = directions.index(self.direction)
        if action == 'turn left':
                new_index = (current_index - 1) % 4 
        else:
                new_index = (current_index + 1) % 4
        self.direction = directions[new_index]

    
    def get_KB_from_percepts(self):
        at_step = len(self.actions)
        look_around = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        current_pos = self.location
        self.visited.add(current_pos)

        percept_names = {p.name for p in self.percepts}

        # negative inferences
        if "stench" not in percept_names:
            for dy, dx in look_around:
                nb = (current_pos[0] + dy, current_pos[1] + dx)
                c = make_clause([Literal("wumpus", nb, True, at_step)])
                if c:
                    self.KB.add(c)
            self.KB.add(make_clause([Literal("stench", tuple(current_pos), True, at_step)]))

        if "breeze" not in percept_names:
            for dy, dx in look_around:
                nb = (current_pos[0] + dy, current_pos[1] + dx)
                c = make_clause([Literal("pit", nb, True, at_step)])
                if c:
                    self.KB.add(c)
            self.KB.add(make_clause([Literal("breeze", tuple(current_pos), True, at_step)]))

        # process each percept
        for percept in self.percepts:
            ppos = tuple(percept.pos)

            if percept.name == 'glitter':
                c = make_clause([Literal("gold", ppos, False, at_step)])
                if c:
                    self.KB.add(c)

            if percept.name == 'stench':
                or_literals = []
                for dy, dx in look_around:
                    nb = (ppos[0] + dy, ppos[1] + dx)
                    or_literals.append(Literal("wumpus", nb, False, at_step))
                    impl = make_clause([Literal("wumpus", nb, True, at_step), Literal("stench", ppos, False, at_step)])
                    if impl:
                        self.KB.add(impl)
                # add the stench literal itself
                or_literals.append(Literal("stench", ppos, True, at_step))
                c = make_clause(or_literals)
                if c:
                    self.KB.add(c)
                self.KB.add(make_clause([Literal("stench", ppos, False, at_step)]))
                self.KB.add(make_clause([Literal("wumpus", ppos, True, at_step), Literal("pit", ppos, True, at_step)]))

            if percept.name == 'breeze':
                or_literals = []
                for dy, dx in look_around:
                    nb = (ppos[0] + dy, ppos[1] + dx)
                    or_literals.append(Literal("pit", nb, False, at_step))
                    impl = make_clause([Literal("pit", nb, True, at_step), Literal("breeze", ppos, False, at_step)])
                    if impl:
                        self.KB.add(impl)
                or_literals.append(Literal("breeze", ppos, True, at_step))
                c = make_clause(or_literals)
                if c:
                    self.KB.add(c)
                self.KB.add(make_clause([Literal("breeze", ppos, False, at_step)]))
                self.KB.add(make_clause([Literal("wumpus", ppos, True, at_step), Literal("pit", ppos, True, at_step)]))

            if percept.name == 'scream':
                die_pos = percept.pos
                c = make_clause([Literal("wumpus", die_pos, True, at_step + 1)])
                if c:
                    self.KB.add(c)

        # Constraint: Pit and Wumpus cannot be in the same cell (¬Pit ∨ ¬Wumpus)
        for dy, dx in look_around:
            pos = (current_pos[0] + dy, current_pos[1] + dx)
            c = make_clause([Literal("pit", pos, True, at_step), Literal("wumpus", pos, True, at_step)])
            if c:
                self.KB.add(c)
        

        # clear percepts
        self.dedupe_latest_dynamic_inplace()
        self.percepts = []

    def dedupe_latest_dynamic_inplace(self):
        latest_time = {}
        for clause in list(self.KB):
            for lit in clause:
                if lit.name in dynamic_literal:
                    key = (lit.name, lit.pos, lit.negate)
                    if key not in latest_time or lit.at_step > latest_time[key]:
                        latest_time[key] = lit.at_step

        new_KB = set()
        for clause in self.KB:
            keep_clause = True
            for lit in clause:
                if lit.name in dynamic_literal:
                    key = (lit.name, lit.pos, lit.negate)
                    if lit.at_step < latest_time[key]:
                        keep_clause = False
                        break
            if keep_clause:
                new_KB.add(clause)
        self.KB = new_KB

    def choose_action(self, mode='random'):
        if mode == 'random':
            '''# Code tĩnh cho wumpus
            result = classify_all_literals(self.KB) 
            for (name, pos), status in sorted(result.items()):
                pos_str = f"({', '.join(map(str, pos))})" if pos else ""
                print(f"{name}{pos_str}: {status}")
            get_action = get_possible_actions(self, result)'''
            # Code động cho wumpus
            current_step = len(self.actions)
            focus_pairs = build_focus_pairs_for_decision(self)          
            result = classify_all_local(self.KB, current_step, focus_pairs)

            get_action = get_possible_actions_now(self, result)
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

    def draw(self, surface):
        origin_x, origin_y = START_MAP_POS
        map_w, map_h = START_MAP_SIZE
        tile = max(1, min(map_w // self.size_known, map_h // self.size_known))

        # cập nhật kích thước sprite cho khớp ô
        self.agent_image.width = tile
        self.agent_image.height = tile

        # (0,0) là góc dưới-trái
        px = origin_x + self.location[1] * tile
        py = origin_y + (self.size_known - 1 - self.location[0]) * tile

        self.agent_image.x = px
        self.agent_image.y = py
        self.agent_image.draw(surface)