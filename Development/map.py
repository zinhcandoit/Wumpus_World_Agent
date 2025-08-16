from Development.definition import Literal
from Development.agent import Agent
from Development.algorithm import make_clause
from Design.ImageManager.Image import Image
from constant import *
import random


class Map:
    def __init__(self, size=4, pit_density=0.2, num_wumpus=2):
        self.size = size
        self.grid = self.generate(size, pit_density, num_wumpus)
        self.rebuild_percept_layers()

        self.wumpus_positions = []
        
        self.ORIGIN_X, self.ORIGIN_Y = START_MAP_POS
        self.MAP_W, self.MAP_H = START_MAP_SIZE
        self.size = size
        self.TILE = self._calc_tile(size)

        self.wumpus_image = Image('assets/wumpus 1.png', self.TILE, self.TILE, 0, 0)
        self.pit_image    = Image('assets/pit.png',    self.TILE, self.TILE, 0, 0)
        self.gold_image   = Image('assets/gold.png',   self.TILE - 10, self.TILE - 10, 0, 0)
        self.stench_image = Image('assets/stench.png', self.TILE, self.TILE, 0, 0)
        self.breeze_image = Image('assets/breeze.png', self.TILE // 3, self.TILE // 3, 0, 0)
        self.tile_image   = Image('assets/tileset/tile.png',   self.TILE, self.TILE, 0, 0)

    def _calc_tile(self, size):
        return max(1, min(self.MAP_W // size, self.MAP_H // size))

    def to_rc(self, y, x):
        return (self.size - 1 - y, x)

    def in_bounds(self, y, x):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_wumpus_actions(self):
        return self.wumpus_pos

    def generate(self, size, pit_density, num_wumpus):
        num_pits = int(size * size * pit_density)
        num_wumpus = min(num_wumpus, size * size - num_pits)
        grid = [[{'NaN'} for _ in range(size)] for _ in range(size)]
        start_pos = (0, 0) 
        all_locations = [(y, x) for y in range(size) for x in range(size) if (y, x) != start_pos]
        pits_pos = random.sample(all_locations, num_pits)
        remaining_locations = [pos for pos in all_locations if pos not in pits_pos]
        wumpus_pos = random.sample(remaining_locations, num_wumpus)
        remaining_locations = [pos for pos in remaining_locations if pos not in wumpus_pos]
        gold_pos = random.choice(remaining_locations)

        for y, x in pits_pos:
            r, c = self.to_rc(y, x)
            grid[r][c] = {'pit'}
        for y, x in wumpus_pos:
            r, c = self.to_rc(y, x)
            grid[r][c] = {'wumpus'}

        r, c = self.to_rc(*gold_pos)
        grid[r][c].add('gold')

        return grid

    def rebuild_percept_layers(self):
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c].discard('breeze')
                self.grid[r][c].discard('stench')

        def add_adjacent_tag(y, x, tag):
            for dy, dx in [(1,0), (-1,0), (0,1), (0,-1)]:
                ny, nx = y + dy, x + dx
                if self.in_bounds(ny, nx):
                    rr, cc = self.to_rc(ny, nx)
                    self.grid[rr][cc].add(tag)

        for y in range(self.size):
            for x in range(self.size):
                r, c = self.to_rc(y, x)
                cell = self.grid[r][c]
                if 'pit' in cell:
                    add_adjacent_tag(y, x, 'breeze')
                if 'wumpus' in cell:
                    add_adjacent_tag(y, x, 'stench')

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
        for dy, dx in [(1,0), (-1,0), (0,1), (0,-1)]:
            ny, nx = y + dy, x + dx
            if self.in_bounds(ny, nx):
                r, c = self.to_rc(ny, nx)
                if element in self.grid[r][c]:
                    return True
        return False

    def update_map(self, action, agent: Agent):
        at_step = len(agent.actions)
        # Di chuyển agent, kiểm tra chết hay nhặt vàng
        if action == "move":
            direction_moves = {'N': (1, 0), 'S': (-1, 0), 'E': (0, 1), 'W': (0, -1)}
            old_y, old_x = agent.location
            dy, dx = direction_moves[agent.direction]
            new_y, new_x = old_y + dy, old_x + dx
            if 'agent' in self.grid[old_y][old_x]:
                self.grid[old_y][old_x].remove('agent')
            agent.location = (new_y, new_x)
            r_new, c_new = self.to_rc(new_y, new_x)
            self.grid[r_new][c_new].discard('NaN')
            self.grid[r_new][c_new].add('agent')
            self.grid[r_new][c_new].add('OK')

            if 'wumpus' in self.grid[r_new][c_new] or 'pit' in self.grid[r_new][c_new]:
                return False

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
                direction_moves = {'N': (1, 0), 'S': (-1, 0), 'E': (0, 1), 'W': (0, -1)}
                dy, dx = direction_moves[agent.direction]
                for i in range(1, self.size):
                    ny = agent.location[0] + i * dy
                    nx = agent.location[1] + i * dx
                    if self.in_bounds(ny, nx):
                        r, c = self.to_rc(ny, nx)
                        if 'wumpus' in self.grid[r][c]:
                            self.grid[r][c].discard('wumpus')
                            self.grid[r][c].add('NaN')
                            agent.wumpus_remain -= 1
                            agent.percepts.append(Literal("scream", agent.wumpus_die, False, at_step))
                            break

        # --- WUMPUS MOVE EVERY 5 STEPS ---
        if at_step % 5 == 0:
            import random
            direction_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E

            # 1) Lấy vị trí wumpus hiện tại
            self.wumpus_positions = []
            for y in range(self.size):
                for x in range(self.size):
                    if 'wumpus' in self.grid[y][x]:
                        self.wumpus_positions.append((y, x))

            # 2) Di chuyển từng con, tránh pit và trùng nhau
            reserved_after_move = set()
            for y, x in self.wumpus_positions:
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

        return True

    def draw(self, surface):
        for y in range(self.size):
            for x in range(self.size):
                row_screen = self.size - 1 - y
                px = self.ORIGIN_X + x * self.TILE
                py = self.ORIGIN_Y + row_screen * self.TILE

                self.tile_image.x = px
                self.tile_image.y = py
                self.tile_image.draw(surface)

                r, c = self.to_rc(y, x)
                cell = self.grid[r][c]

                if 'pit' in cell:
                    self.pit_image.x = px
                    self.pit_image.y = py
                    self.pit_image.draw(surface)
                if 'wumpus' in cell:
                    self.wumpus_image.x = px
                    self.wumpus_image.y = py
                    self.wumpus_image.draw(surface)
                if 'gold' in cell:
                    self.gold_image.x = px
                    self.gold_image.y = py
                    self.gold_image.draw(surface)
                if 'stench' in cell:
                    self.stench_image.x = px
                    self.stench_image.y = py
                    self.stench_image.draw(surface)
                if 'breeze' in cell:
                    self.breeze_image.x = px
                    self.breeze_image.y = py
                    self.breeze_image.draw(surface)
