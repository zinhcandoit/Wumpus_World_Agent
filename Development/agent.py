from Development.definition import Literal
import random
from Development.algorithm import *
from heapq import heappush, heappop

from heapq import heappush, heappop
class Agent:
    def __init__(self, num_w=2, map_size=None):
        self.start_location = (map_size - 1, 0)
        self.location = (map_size - 1, 0)
        self.w_remain = num_w
        self.actions = []
        self.direction = 'E'
        self.has_gold = False
        self.has_arrow = True
        self.w_die = None
        self.size_known = map_size
        self.visited = set()
        self.percepts = [] # New percepts at current location
        self.KB = set()
        self.current_plan = [] # Plan for actions
        self.last_loc = None
    
    def update_direction(self, action):
        directions = ['N', 'E', 'S', "W"]
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

        self.KB.add(make_clause([Literal("wumpus", tuple(current_pos), True, at_step)]))
        self.KB.add(make_clause([Literal("pit", tuple(current_pos), True, at_step)]))
        # negative inferences
        # No adding -stench and -breeze here to KB
        if "stench" not in percept_names:
            for dy, dx in look_around:
                nb = (current_pos[0] + dy, current_pos[1] + dx)
                if 0 <= nb[0] < self.size_known and 0 <= nb[0] < self.size_known:
                    c = make_clause([Literal("wumpus", nb, True, at_step)])
                    if c:
                        self.KB.add(c)
                if 0 <= nb[0] < self.size_known and 0 <= nb[1] < self.size_known:
                    c = make_clause([Literal("wumpus", nb, True, at_step)])
                    if c:
                        self.KB.add(c)
            self.KB.add(make_clause([Literal('stench', self.location, True, at_step)]))

        if "breeze" not in percept_names:
            for dy, dx in look_around:
                nb = (current_pos[0] + dy, current_pos[1] + dx)
                if 0 <= nb[0] < self.size_known and 0 <= nb[0] < self.size_known:
                    c = make_clause([Literal("pit", nb, True, at_step)])
                    if c:
                        self.KB.add(c)
                if 0 <= nb[0] < self.size_known and 0 <= nb[1] < self.size_known:
                    c = make_clause([Literal("pit", nb, True, at_step)])
                    if c:
                        self.KB.add(c)
            self.KB.add(make_clause([Literal('breeze', self.location, True, at_step)]))
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
                    if 0 <= nb[0] < self.size_known and 0 <= nb[1] < self.size_known: 
                        or_literals.append(Literal("wumpus", nb, False, at_step))
                        impl = make_clause([Literal("wumpus", nb, True, at_step), Literal("stench", ppos, False, at_step)])
                        if impl:
                            self.KB.add(impl)
                    if 0 <= nb[0] < self.size_known and 0 <= nb[1] < self.size_known: 
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
                    if 0 <= nb[0] < self.size_known and 0 <= nb[1] < self.size_known: 
                        or_literals.append(Literal("pit", nb, False, at_step))
                        impl = make_clause([Literal("pit", nb, True, at_step), Literal("breeze", ppos, False, at_step)])
                        if impl:
                            self.KB.add(impl)
                    if 0 <= nb[0] < self.size_known and 0 <= nb[1] < self.size_known: 
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

        # Constraint: p and w cannot be in the same cell (¬p ∨ ¬w)
        for dy, dx in look_around:
            pos = (current_pos[0] + dy, current_pos[1] + dx)
            if 0 <= pos[0] < self.size_known and 0 <= pos[1] <self.size_known:
                c = make_clause([Literal("pit", pos, True, at_step), Literal("wumpus", pos, True, at_step)])
                if c:
                    self.KB.add(c)
        

        # clear percepts
        self.dedupe_latest_dynamic_inplace()
        self.percepts = []

    def dedupe_latest_dynamic_inplace(self):
        t = len(self.actions)
        latest_any = {}
        latest_no_wumpus = {}

        for clause in self.KB:
            for lit in clause:
                if lit.name in dynamic_literal:
                    k = (lit.name, lit.pos)
                    if lit.at_step > latest_any.get(k, -1):
                        latest_any[k] = lit.at_step
                if lit.name == 'wumpus' and lit.negate:
                    if lit.pos not in latest_no_wumpus or lit.at_step > latest_no_wumpus[lit.pos]:
                        latest_no_wumpus[lit.pos] = lit.at_step

        # Drop older wumpus clause
        new_KB = set()
        for clause in self.KB:
            outdated = any(
                (lit.name in dynamic_literal) and
                (lit.at_step < latest_any.get((lit.name, lit.pos), lit.at_step))
                for lit in clause
            )
            if not outdated:
                new_KB.add(clause)
        self.KB = new_KB

        # Keep no wumpus clauses
        if t > 0 and t % 5 == 0:
            self.KB = {clause for clause in self.KB
                    if not any((lit.name == 'stench') and (lit.at_step < t) for lit in clause)}

        any_stench_at_t = any(lit.name == 'stench' and lit.negate == False and lit.at_step == t
                      for clause in self.KB for lit in clause)

        if self.actions and self.actions[-1] == 'move' and (t % 5) != 0 and any_stench_at_t == False and latest_no_wumpus:
            # No wumpus at time t - n => no wumpus at time t 
            existing_neg_t = {lit.pos for clause in self.KB for lit in clause
                            if (lit.name == 'wumpus') and lit.negate and lit.at_step < t}
            for pos, step in latest_no_wumpus.items():
                if step != t and pos not in existing_neg_t:
                    c = make_clause([Literal('wumpus', pos, True, t)])
                    if c:
                        self.KB.add(c)

    @staticmethod
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    
    @staticmethod
    def turn_cost(curr_dir, target_dir):
        directions = ['N', 'E', 'S', 'W']
        idx_curr = directions.index(curr_dir)
        idx_target = directions.index(target_dir)

        diff = (idx_target - idx_curr) % 4  

        steps = []
        if diff == 0:
            steps.append("move")
            return (1, tuple(steps))
        elif diff == 1:
            steps.extend(["turn right", "move"])
            return (2, tuple(steps))
        elif diff == 2:
            steps.extend(["turn right", "turn right", "move"])
            return (3, tuple(steps))
        elif diff == 3:
            steps.extend(["turn left", "move"])
            return (2, tuple(steps))

    def neighbor_cells(self, loc):
        neighbors = {
            'E': (loc[0], loc[1] + 1),
            'W': (loc[0], loc[1] - 1),
            'N': (loc[0] - 1, loc[1]),
            'S': (loc[0] + 1, loc[1])
        }

        # loại bỏ ô ngoài map
        for dir, pos in list(neighbors.items()):
            if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.size_known or pos[1] >= self.size_known:
                neighbors.pop(dir)
        
        return neighbors

    def find_next_action(self):
        if self.current_plan:
            return self.current_plan.pop(0)

        # Get cell states from KB
        current_step = len(self.actions)
        focus_pairs = build_focus_pairs_for_decision(self)
        cell_states = classify_all_local(self.KB, current_step, focus_pairs)

        safe, unsafe = set(), set()
        grouped = {}
        for (name, pos), state in cell_states.items():
            grouped.setdefault(pos, {})[name] = state

        for pos, facts in grouped.items():
            if facts.get("pit") == "SAFE" and facts.get("wumpus") == "SAFE":
                safe.add(pos)
            elif facts.get("pit") == "UNSAFE" or facts.get("wumpus") == "UNSAFE":
                unsafe.add(pos)

        # Visited is safe, previous location is not unsafe
        safe |= self.visited
        if self.last_loc:
            unsafe.remove(self.last_loc)

        rows = cols = self.size_known
        unvisited = {(r, c) for r in range(rows) for c in range(cols)
                    if (r, c) not in self.visited and (r, c) not in unsafe}

        # Get neighbor cells and possible action
        neighbors = self.neighbor_cells(self.location)
        actions = get_possible_actions_now(self, cell_states)

        if 'grab' in actions:
            return 'grab'
        if 'shoot' in actions and self.has_arrow:
            return 'shoot'
        if self.has_gold:
            if self.location == self.start_location and 'climb out' in actions:
                return 'climb out'
            self.current_plan = self.plan_path(self.location, self.direction, self.start_location, safe)
            if self.current_plan:
                return self.current_plan.pop(0)

        # Choose safe location by A*
        # Get safe neighbor that not in visited
        candidates = [cell for cell in neighbors.values() if cell in safe and cell not in self.visited]

        # If not, expand it
        if not candidates:
            for cell in neighbors.values():
                if cell in self.visited and cell in safe:
                    for c in self.neighbor_cells(cell).values():
                        if c not in self.visited:
                            candidates.append(c)

        # Get goal pos
        reachable = []
        for target in candidates:
            plan = self.plan_path(self.location, self.direction, target, safe)
            if plan:
                reachable.append((target, plan))

        if reachable:
            target, plan = min(reachable, key=lambda x: (len(x[1]), self.heuristic(self.location, x[0])))
            self.current_plan = plan
            return self.current_plan.pop(0)

        # Expand frontier
        progress = len(self.visited) + len(unsafe)
        total = self.size_known * self.size_known
        if (progress / total) < 0.9:
            frontier = []
            for v in unvisited:
                plan = self.plan_path(self.location, self.direction, v, safe)
                if plan:
                    frontier.append((v, plan))
            if frontier:
                target, plan = min(frontier, key=lambda x: (len(x[1]), self.heuristic(self.location, x[0])))
                self.current_plan = plan
                return self.current_plan.pop(0)

        # Fall back (get last loc to avoid ping pong movement)
        prev_loc = getattr(self, '_last_loc', None)
        y, x = self.location
        direction_moves = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
        dy, dx = direction_moves[self.direction]
        front_cell = (y + dy, x + dx)

        can_move_forward = ('move' in actions) and (front_cell not in unsafe)
        if prev_loc is not None and front_cell == prev_loc:
            can_move_forward = False

        # tier list: move -> turn left -> turn right
        if can_move_forward:
            action = 'move'
        elif 'turn left' in actions:
            action = 'turn left'
        elif 'turn right' in actions:
            action = 'turn right'
        else:
            action = 'turn left' if 'turn left' in actions else ('turn right' if 'turn right' in actions else 'move')

        # Store that location for next call
        self._last_loc = self.location
        return action
            
            
    def plan_path(self, start, start_dir, goal, safe_cells):
        """
        Tìm đường đi bằng A* từ start -> goal qua các safe_cells.
        Trả về list action: ["turn left", "move", ...]
        """

        directions = ['N', 'E', 'S', 'W']
        moves = {'N': (-1,0), 'E': (0,1), 'S': (1,0), 'W': (0,-1)}

        start_state = (start, start_dir)
        frontier = []
        heappush(frontier, (0, start_state, []))
        visited = set()
        forbid_first = getattr(self, '_last_loc', None)

        while frontier:
            cost, (pos, facing), path = heappop(frontier)
            if pos == goal:
                return path
            if (pos, facing) in visited:
                continue
            visited.add((pos, facing))

            for d in directions:
                dy, dx = moves[d]
                new_pos = (pos[0]+dy, pos[1]+dx)
                if new_pos not in safe_cells:
                    continue
                if not path and forbid_first is not None and new_pos == forbid_first:
                    continue
                turn_steps_cost, turn_steps = self.turn_cost(facing, d)
                new_path = path + list(turn_steps)
                new_cost = cost + turn_steps_cost
                heappush(frontier, (new_cost + self.heuristic(new_pos, goal),
                                (new_pos, d), new_path))      

        return []

    def choose_action(self, mode='random'):
        if mode == 'random':
            current_step = len(self.actions)
            focus_pairs = build_focus_pairs_for_decision(self)          
            result = classify_all_local(self.KB, current_step, focus_pairs)

            get_action = get_possible_actions_now(self, result)
            print("Possible actions:", get_action)
            if 'grab' in get_action:
                return 'grab'
            if 'move' in get_action and random.randint(1, 2) == 2:
                return 'move'
            if 'climb out' in get_action and self.has_gold:
                return 'climb out'
            elif 'climb out' in get_action: get_action.remove('climb out')
            if 'shoot' in get_action and self.has_arrow:
                return 'shoot'
            return get_action.pop(random.randint(0, len(get_action) - 1))
        elif mode == 'logic':

            get_action = self.find_next_action()
            return get_action