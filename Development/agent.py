from Development.definition import Literal
import random
from Development.algorithm import *
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
            self.KB.add(make_clause([Literal("stench", tuple(current_pos), True, at_step)]))

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
                    if 0 <= nb[0] < self.size_known and 0 <= nb[0] < self.size_known: 
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
                    if 0 <= nb[0] < self.size_known and 0 <= nb[0] < self.size_known: 
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
        
    def select_goal(self, safe, unsafe, candidates):
        """
        Chọn goal động dựa trên trạng thái hiện tại
        """
        # Nếu có vàng rồi -> ưu tiên thoát
        if self.has_gold:
            return self.start_location

        # Nếu còn ô an toàn chưa khám phá -> tiếp tục explore
        if candidates:
            # chọn ô gần nhất để khám phá
            return min(candidates, key=lambda c: self.heuristic(self.location, c))

        # Nếu không còn gì để explore -> quay về start
        return self.start_location

    
    def find_next_action(self):
        """
        Chọn hành động tiếp theo cho Agent dựa trên A* và KB.
        Agent không cần biết trước map size cho đến khi gặp bump.
        """

        if self.current_plan:
            return self.current_plan.pop(0)

        # ========== 1. Lấy trạng thái KB ==========
        current_step = len(self.actions)
        focus_pairs = build_focus_pairs_for_decision(self)
        cell_states = classify_all_local(self.KB, current_step, focus_pairs)

        safe, unsafe = set(), set()

        grouped = {}
        for (name, pos), state in cell_states.items():
            if pos not in grouped:
                grouped[pos] = {}
            grouped[pos][name] = state

        for pos, facts in grouped.items():
            if facts.get("pit") == "SAFE" and facts.get("wumpus") == "SAFE":
                safe.add(pos)
            else: unsafe.add(pos)

        safe |= self.visited
        unsafe -= self.visited

        for pos, facts in grouped.items():
            if facts.get("pit") == "UNSAFE" or facts.get("wumpus") == "UNSAFE":
                unsafe.add(pos)

        # ========== 2. Tìm neighbors ==========
        neighbors = {
            'E': (self.location[0], self.location[1] + 1),
            'W': (self.location[0] , self.location[1] - 1),
            'N': (self.location[0] - 1, self.location[1]),
            'S': (self.location[0] + 1, self.location[1])
            }

        # Loại bỏ ô ngoài map
        for dir, pos in list(neighbors.items()):
            if pos[0] < 0 or pos[1] < 0 or pos[0] > self.size_known - 1 or pos[1] > self.size_known - 1:
                neighbors.pop(dir)
        
        actions = get_possible_actions_now(self, cell_states)

        # ========== 3. Chiến lược ==========
        # 3.1 Nếu đang đứng trên vàng -> nhặt
        if 'grab' in actions:
            return 'grab'

        # 3.2 Nếu đã có vàng -> tìm đường về start
        if self.has_gold:
            if self.location == self.start_location and 'climb out' in actions:
                return 'climb out'
            goal = self.start_location  # luôn về start
            self.current_plan = self.plan_path(self.location, self.direction, goal, safe)
            if self.current_plan:
                return self.current_plan.pop(0)

        # 3.3 Nếu chưa có vàng -> tìm safe cell chưa thăm
        candidates = []
        for cell in safe:
            if cell not in self.visited:
                candidates.append(cell)
            else:
            # check neighbors của chính cell đó
                cx, cy = cell
                neighbor_cells = [
                    (cx+1, cy), (cx-1, cy),
                    (cx, cy+1), (cx, cy-1)
                ]
                for n in neighbor_cells:
                    if n in safe and n not in self.visited:
                        candidates.append(cell)
                        break

        if candidates:
            # duyệt lần lượt từ gần đến xa
            for target in sorted(candidates, key=lambda c: self.heuristic(self.location, c)):
                plan = self.plan_path(self.location, self.direction, target, safe)
                if plan:
                    self.current_plan = plan
                    return self.current_plan.pop(0)
            

        # 3.4 Nếu hết đường đi -> thoát
        if self.location == self.start_location:
            return "climb out"
        else:
            # fallback: quay lại start
            plan = self.plan_path(self.location, self.direction, self.start_location, safe)
            if plan:
                self.current_plan = plan
                return self.current_plan.pop(0)
            return "climb out"
    
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
                turn_steps_cost, turn_steps = self.turn_cost(facing, d)
                new_path = path + list(turn_steps)
                new_cost = cost + turn_steps_cost
                heappush(frontier, (new_cost + self.heuristic(new_pos, goal),
                                (new_pos, d), new_path))
                
        for d in directions:
            dy, dx = moves[d]
            back_pos = (start[0]+dy, start[1]+dx)
            if back_pos in self.visited and back_pos in safe_cells:
                # tìm plan quay về back_pos
                return self.plan_path(start, start_dir, back_pos, safe_cells)        

        return []

    def choose_action(self, mode='random'):
        if mode == 'random':
            '''# Code tĩnh cho w
            result = classify_all_literals(self.KB) 
            for (name, pos), status in sorted(result.items()):
                pos_str = f"({', '.join(map(str, pos))})" if pos else ""
                print(f"{name}{pos_str}: {status}")
            get_action = get_possible_actions(self, result)'''
            # Code động cho w
            current_step = len(self.actions)
            focus_pairs = build_focus_pairs_for_decision(self)          
            result = classify_all_local(self.KB, current_step, focus_pairs)

            # for (name, pos), status in sorted(result.items()):
            #     pos_str = f"({', '.join(map(str, pos))})" if pos else ""
            #     print(f"{name}{pos_str}: {status}")

            get_action = get_possible_actions_now(self, result)
            print("Possible actions:", get_action)
            if 'grab' in get_action:
                return 'grab'
            if 'move' in get_action and random.random() <= 0.7:
                return 'move'
            if 'climb out' in get_action and self.has_gold:
                return 'climb out'
            elif 'climb out' in get_action: get_action.remove('climb out')
            if 'shoot' in get_action and self.has_arrow:
                return 'shoot'
            return get_action.pop(random.randint(0, len(get_action) - 1))
        elif mode == 'logic':
            '''# Code tĩnh cho w
            result = classify_all_literals(self.KB) 
            for (name, pos), status in sorted(result.items()):
                pos_str = f"({', '.join(map(str, pos))})" if pos else ""
                print(f"{name}{pos_str}: {status}")
            get_action = get_possible_actions(self, result)'''
            # Code động cho w

            get_action = self.find_next_action()
            return get_action