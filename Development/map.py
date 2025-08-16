from Development.definition import Literal
import random
from Development.agent import Agent
from Development.algorithm import make_clause
from Design.ImageManager.Image import Image
class Map:
    def __init__(self, size = 4, pit_density = 0.2, num_wumpus = 2):
        self.size = size
        self.grid = self.generate(size, pit_density, num_wumpus)

        # self.wumpus_image = Image('Images/wumpus.png', 50, 50, 0, 0)
        # self.pit_image = Image('Images/pit.png', 50, 50, 0, 0)
        # self.gold_image = Image('Images/gold.png', 50, 50, 0, 0)
        # self.stench_image = Image('Images/stench.png', 50, 50, 0, 0)
        # self.breeze_image = Image('Images/breeze.png', 50, 50, 0, 0)
        # self.map_image = Image('Images/map.png', 500, 500, 0, 0)

    def generate(self, size, pit_density, num_wumpus):
        num_pits = int(size * size * pit_density)
        num_wumpus = min(num_wumpus, size ** 2 - num_pits - 1)
        grid = [[{'NaN'} for _ in range(size)] for _ in range(size)]
        start_pos = (-1, 0)
        all_locations = [(i, j) for i in range(size) for j in range(size) if (i - size, j) != start_pos]
        pits_pos = random.sample(all_locations, num_pits)
        remaining_locations = [pos for pos in all_locations if pos not in pits_pos]
        wumpus_pos = random.sample(remaining_locations, num_wumpus)
        for x, y in pits_pos:
            grid[x][y] = {'pit'}
        for x, y in wumpus_pos:
            grid[x][y] = {'wumpus'}
        gold_pos = random.choice(remaining_locations)
        grid[gold_pos[0]][gold_pos[1]].add('gold')
        grid[start_pos[0]][start_pos[1]] = {'agent', 'OK'}
        return grid

    def get_percepts_for_agent(self, agent: Agent):
        y, x = agent.location
        at_step = len(agent.actions)

        percepts = []

        if 'gold' in self.grid[y][x]:
            percepts.append(Literal("glitter", (y, x), False, at_step))

        if self.has_adjacent(y, x, 'wumpus'):
            percepts.append(Literal("stench", (y, x), False, at_step))

        if self.has_adjacent(y, x, 'pit'):
            percepts.append(Literal("breeze", (y, x), False, at_step))
        return percepts
    
    def has_adjacent(self, y, x, element):
        # kiểm tra 4 hướng lân cận có element không
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dy, dx in directions:
            if 0 <= x + dx < self.size and 0 <= y + dy < self.size:
                if element in self.grid[y + dy][x + dx]:
                    return True
        return False

    def update_map(self, action, agent: Agent):
        at_step = len(agent.actions)
        # --- WUMPUS MOVE EVERY 5 STEPS ---
        if at_step % 5 == 0:
            import random
            direction_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E

            # 1) Lấy vị trí wumpus hiện tại
            wumpus_positions = []
            for y in range(self.size):
                for x in range(self.size):
                    if 'wumpus' in self.grid[y][x]:
                        wumpus_positions.append((y, x))

            # 2) Di chuyển từng con, tránh pit và trùng nhau
            reserved_after_move = set()
            for y, x in wumpus_positions:
                dirs = direction_moves[:]
                random.shuffle(dirs)
                moved = False

                for dy, dx in dirs:
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < self.size and 0 <= nx < self.size):
                        continue
                    # Không được trùng pit, Không được vướng lẫn nhau
                    if 'pit' in self.grid[ny][nx]:
                        continue
                    if 'wumpus' in self.grid[ny][nx]:
                        continue
                    if (ny, nx) in reserved_after_move:
                        continue

                    # --- COMMIT MOVE ---
                    self.grid[y][x].discard('wumpus')
                    if ('OK' not in self.grid[y][x]):
                        self.grid[y][x].add('NaN')
                    self.grid[ny][nx].discard('NaN')
                    self.grid[ny][nx].add('wumpus')
                    moved = True
                    # Nếu wumpus vừa tới ô có agent -> agent chết
                    if (ny, nx) == agent.location:
                        return False

                    reserved_after_move.add((ny, nx))
                    break

                if not moved:
                    reserved_after_move.add((y, x))
        # Di chuyển agent, kiểm tra chết hay nhặt vàng
        if action == "move":
            direction_moves = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
            old_y, old_x = agent.location
            dy, dx = direction_moves[agent.direction]
            new_y, new_x = old_y + dy, old_x + dx
            if 'agent' in self.grid[old_y][old_x]:
                self.grid[old_y][old_x].remove('agent')
            agent.location = (new_y, new_x)
            self.grid[new_y][new_x].discard('NaN')
            self.grid[new_y][new_x].add('agent')
            self.grid[new_y][new_x].add('OK')
            if 'wumpus' in self.grid[new_y][new_x] or 'pit' in self.grid[new_y][new_x]:
                return False  # Agent dies
        elif action == "turn left":
            agent.update_direction('turn left')
    
        elif action == "turn right":
            agent.update_direction('turn right')
        elif action == "grab":
            if 'gold' in self.grid[agent.location[0]][agent.location[1]]:
                agent.has_gold = True
                # Remove gold from KB
                agent.KB.remove(make_clause([Literal("gold", agent.location, False, at_step - 1)]))
                self.grid[agent.location[0]][agent.location[1]].discard('gold')
        elif action == "shoot":
            if agent.has_arrow:
                agent.has_arrow = False
                direction_moves = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
                dy, dx = direction_moves[agent.direction]
                for i in range(1, self.size):
                    new_y, new_x = agent.location[0] + i * dy, agent.location[1] + i * dx
                    if 0 <= new_y < self.size and 0 <= new_x < self.size:
                        if 'wumpus' in self.grid[new_y][new_x]:
                            self.grid[new_y][new_x].discard('wumpus')
                            self.grid[new_y][new_x].add('NaN')
                            agent.wumpus_remain -= 1
                            agent.percepts.append(Literal("scream", agent.wumpus_die, False, at_step))
                            break

        return True
    
    # def draw():
    #     pass


             
