import pygame
from Screen.BaseScreen import Screen
from Design.UI.text import Text
from Design.UI.slider import Slider
from Design.UI.button import Button
from Design.UI.toggle import Toggle
from Design.ImageManager.Image import Image
from Development.gameState import Game
from constant import *
import time

class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)

        self.map_size = 8
        self.pit_density = 0.2
        self.num_wumpus = 2
        self.hard_mode = False

        self.Game = None
        self.game_finished = False
        self.solved_point = None
        self.solved_actions = []

        # Animation state
        self.is_animating = False
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 1000  # milliseconds per step
        self.animation_paused = False
        self.agent_position = (0, 0)  # (row, col)
        self.agent_direction = "right"  # right, left, up, down
        self.current_game_state = None

        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2

        # Thêm scroll cho actions list
        self.actions_scroll_y = 0
        self.max_actions_display = 6
        self.action_line_height = 25

        self.slider_list = [
            {"label": "Map Size:", "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12), "label_pos": (self.ui_panel_x + 20, 140)},
            {"label": "Pit Density:", "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5), "label_pos": (self.ui_panel_x + 20, 220)},
            {"label": "Number of Wumpus:", "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5), "label_pos": (self.ui_panel_x + 20, 300)},
        ]

        button_width = self.ui_panel_width - 40
        self.start_btn = Button("Start", "Arial", button_width, 40, self.ui_center_x, 440, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.back_btn  = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_RED, Color.WHITE, "body", "center")
        
        # Animation control buttons
        self.play_btn = Button("Play Animation", "Arial", button_width, 30, self.ui_center_x, 540, Color.BLUE, Color.WHITE, "small", "center")
        self.pause_btn = Button("Pause", "Arial", button_width//2 - 5, 30, self.ui_center_x - button_width//4, 580, Color.ORANGE, Color.WHITE, "small", "center")
        self.reset_btn = Button("Reset", "Arial", button_width//2 - 5, 30, self.ui_center_x + button_width//4, 580, Color.GRAY, Color.WHITE, "small", "center")

        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)

        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.ui_panel_x + 20, 390, "left", "body")

        # Speed control
        self.speed_label = Text("Speed:", "Arial", Color.WHITE, self.ui_panel_x + 20, 620, "left", "small")
        self.speed_slider = Slider(self.ui_center_x, 625, self.ui_panel_width // 3 + 20, 15, 1.0, 0.2, 3.0)

        # Actions display area
        self.actions_title = Text("Actions Sequence:", "Arial", Color.YELLOW, self.ui_panel_x + 20, 650, "left", "body")
        self.current_action_text = Text("", "Arial", Color.LIME, self.ui_panel_x + 20, 675, "left", "body")

        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

        self.agent_image = Image("assets/agent.png") 
        self.tile_image = Image("assets/tileset/tile.png")
        self.pit_image = Image("assets/pit.png")
        self.gold_image = Image("assets/gold.png")
        self.wumpus_image = Image("assets/wumpus 1.png")
        self.stench_image = Image("assets/stench.png")
        self.breeze_image = Image("assets/breeze.png")

        # Create rotated agent images for different directions
        self.agent_images = {}

    def create_rotated_agent_images(self, cell_size):
        if cell_size not in self.agent_images:
            base_img = pygame.transform.smoothscale(self.agent_image.image, (cell_size, cell_size))
            self.agent_images[cell_size] = {
                "right": base_img,
                "left": pygame.transform.flip(base_img, True, False),
                "up": pygame.transform.rotate(base_img, 90),
                "down": pygame.transform.rotate(base_img, -90)
            }

    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_title(self, surface):
        self.title.draw(surface)

    def draw_ui_panel_background(self, surface):
        panel_surface = pygame.Surface((self.ui_panel_width, SCREEN_HEIGHT))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(150)
        surface.blit(panel_surface, (self.ui_panel_x, 0))

    def draw_animation_controls(self, surface):
        if self.game_finished and self.solved_actions:
            if not self.is_animating:
                self.play_btn.draw(surface)
            
            self.pause_btn.draw(surface)
            self.reset_btn.draw(surface)
            
            # Speed control
            self.speed_label.draw(surface)
            self.speed_slider.draw(surface)
            
            # Animation progress
            progress_text = f"Progress: {min(self.animation_index + 1, len(self.solved_actions))}/{len(self.solved_actions)}"
            progress_display = Text(progress_text, "Arial", Color.CYAN, self.ui_panel_x + 20, 675, "left", "small")
            progress_display.draw(surface)

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_ui_panel_background(surface)
        self.draw_title(surface)

        for item in self.slider_list:
            Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body").draw(surface)
            item["slider"].draw(surface)

        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        # Status text
        if self.game_finished and self.solved_point is not None:
            if self.is_animating:
                msg = f"Animating... Point: {self.solved_point}"
            else:
                msg = f"Solved! Actions: {len(self.solved_actions)}, Point: {self.solved_point}"
        else:
            msg = "Ready to start"
        self.status_text.text = msg
        self.status_text.draw(surface)

        self.start_btn.draw(surface)
        self.back_btn.draw(surface)

        self.draw_animation_controls(surface)

        if self.Game:
            self.draw_game_map(surface)

    def start_game(self):
        size = int(self.slider_list[0]["slider"].value)
        pit = self.slider_list[1]["slider"].value
        wumpus = int(self.slider_list[2]["slider"].value)
        hard = self.toggle.value

        print("Game configuration:", size, pit, wumpus, hard)

        # Reset trạng thái
        self.game_finished = False
        self.solved_point = None
        self.solved_actions = []
        self.reset_animation()

        # Khởi tạo game và gọi solver đồng bộ
        self.Game = Game(size, pit, wumpus, hard)
        self.agent_position = (size - 1, 0)  # Start position (bottom-left)
        self.agent_direction = "right"  # Start facing right
        self.current_game_state = self.copy_game_state()

        point, actions = self.Game.play()

        # Lưu kết quả
        self.solved_point = point
        self.solved_actions = actions or []
        self.game_finished = True

        print("Point:", point)
        print("Actions:", self.solved_actions)

    def copy_game_state(self):
        """Sao chép trạng thái game hiện tại"""
        if not self.Game or not hasattr(self.Game, "map"):
            return None
        
        # Tạo bản sao của grid - xử lý set objects
        grid = []
        for row in self.Game.map.grid:
            new_row = []
            for cell in row:
                if isinstance(cell, set):
                    new_row.append(cell.copy())
                elif isinstance(cell, list):
                    new_row.append(cell[:])
                else:
                    new_row.append(cell)
            grid.append(new_row)
        
        return {
            "grid": grid,
            "agent_pos": self.agent_position,
            "agent_direction": self.agent_direction
        }

    def start_animation(self):
        """Bắt đầu animation"""
        if self.game_finished and self.solved_actions:
            self.is_animating = True
            self.animation_paused = False
            self.animation_timer = pygame.time.get_ticks()
            # Reset về trạng thái ban đầu
            if self.animation_index == 0:
                self.reset_to_initial_state()

    def pause_animation(self):
        if self.is_animating:
            self.animation_paused = not self.animation_paused
            if not self.animation_paused:
                self.animation_timer = pygame.time.get_ticks()

    def reset_animation(self):
        self.is_animating = False
        self.animation_paused = False
        self.animation_index = 0
        self.animation_timer = 0
        if self.Game:
            size = len(self.Game.map.grid) if hasattr(self.Game, "map") else 8
            self.agent_position = (size - 1, 0)
            self.agent_direction = "right"  

    def reset_to_initial_state(self):
        if not self.Game:
            return
        
        size = len(self.Game.map.grid)
        self.agent_position = (size - 1, 0)  
        self.agent_direction = "right"  
    
    def update_animation(self):
        if not self.is_animating or self.animation_paused:
            return
        
        current_time = pygame.time.get_ticks()
        speed_multiplier = self.speed_slider.value
        step_duration = max(200, int(self.animation_speed / speed_multiplier))
        
        if current_time - self.animation_timer >= step_duration:
            if self.animation_index < len(self.solved_actions):
                self.execute_animation_step()
                self.animation_index += 1
                self.animation_timer = current_time
            else:
                self.is_animating = False

    def execute_animation_step(self):
        if self.animation_index >= len(self.solved_actions):
            return
        
        action = self.solved_actions[self.animation_index]
        action_lower = action.lower().strip()
        
        row, col = self.agent_position
        
        if action_lower == "move":
            if self.agent_direction == "up":
                self.agent_position = (max(0, row - 1), col)
            elif self.agent_direction == "down":
                self.agent_position = (min(len(self.Game.map.grid) - 1, row + 1), col)
            elif self.agent_direction == "left":
                self.agent_position = (row, max(0, col - 1))
            elif self.agent_direction == "right":
                self.agent_position = (row, min(len(self.Game.map.grid[0]) - 1, col + 1))
        
        elif "turn left" in action_lower:
            direction_map = {"right": "up", "up": "left", "left": "down", "down": "right"}
            self.agent_direction = direction_map.get(self.agent_direction, self.agent_direction)
        
        elif "turn right" in action_lower:
            direction_map = {"right": "down", "down": "left", "left": "up", "up": "right"}
            self.agent_direction = direction_map.get(self.agent_direction, self.agent_direction)
        
        # print(f"Animation step {self.animation_index + 1}: {action} -> Position: {self.agent_position}, Direction: {self.agent_direction}")

    def update(self):
        for item in self.slider_list:
            item["slider"].update()
        self.toggle.update()
        
        if self.game_finished:
            self.speed_slider.update()
        
        self.update_animation()

    def draw_game_map(self, surface):
        if not self.Game or not hasattr(self.Game, "map") or not hasattr(self.Game.map, "grid"):
            return

        grid = self.Game.map.grid
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if rows == 0 or cols == 0:
            return

        # Vùng vẽ bên trái panel
        map_area_w = SCREEN_WIDTH - self.ui_panel_width
        map_area_h = SCREEN_HEIGHT
        margin = 20

        cell_size = max(1, min(
            (map_area_w - 2 * margin) // cols,
            (map_area_h - 2 * margin) // rows
        ))
        origin_x = margin
        origin_y = (map_area_h - rows * cell_size) // 2

        # Tạo rotated agent images
        self.create_rotated_agent_images(cell_size)

        # Cache scale theo cell_size
        if not hasattr(self, "_scaled_cache"):
            self._scaled_cache = {}
        def _scale(img_obj):
            key = (id(img_obj), cell_size)
            if key not in self._scaled_cache:
                self._scaled_cache[key] = pygame.transform.smoothscale(
                    img_obj.image, (cell_size, cell_size)
                )
            return self._scaled_cache[key]

        tile_img   = _scale(self.tile_image)
        gold_img   = _scale(self.gold_image)
        pit_img     = _scale(self.pit_image)
        wumpus_img = _scale(self.wumpus_image)
        stench_img = _scale(self.stench_image)
        breeze_img = _scale(self.breeze_image)

        token_to_img = {
            "gold": gold_img,
            "wumpus": wumpus_img,
            "pit": pit_img,
            "stench": stench_img,
            "breeze": breeze_img,
        }

        # Vẽ lưới
        grid_color = (40, 40, 40)
        for r in range(rows + 1):
            y = origin_y + r * cell_size
            pygame.draw.line(surface, grid_color, (origin_x, y), (origin_x + cols * cell_size, y), 1)
        for c in range(cols + 1):
            x = origin_x + c * cell_size
            pygame.draw.line(surface, grid_color, (x, origin_y), (x, origin_y + rows * cell_size), 1)

        # Vẽ map
        for r in range(rows):
            for c in range(cols):
                x = origin_x + c * cell_size
                y = origin_y + r * cell_size
                surface.blit(tile_img, (x, y))

                # Vẽ các token trừ agent
                for tok in grid[r][c]:
                    if tok != "agent":
                        img = token_to_img.get(tok)
                        if img:
                            surface.blit(img, (x, y))

        # Vẽ agent ở vị trí hiện tại với hướng đúng
        if self.game_finished and self.is_animating:
            agent_row, agent_col = self.agent_position
            agent_x = origin_x + agent_col * cell_size
            agent_y = origin_y + agent_row * cell_size
            
            agent_img = self.agent_images[cell_size][self.agent_direction]
            surface.blit(agent_img, (agent_x, agent_y))
        else:
            # Vẽ agent ở vị trí trong grid gốc
            for r in range(rows):
                for c in range(cols):
                    if "agent" in grid[r][c]:
                        x = origin_x + c * cell_size
                        y = origin_y + r * cell_size
                        agent_img = self.agent_images.get(cell_size, {}).get("right", _scale(self.agent_image))
                        surface.blit(agent_img, (x, y))

    def handle_event(self, event):
        if not self.Game or self.game_finished:
            for item in self.slider_list:
                item["slider"].handle_event(event)
            self.toggle.handle_event(event)
        
        if self.game_finished:
            self.speed_slider.handle_event(event)

        # Xử lý scroll cho actions list
        if self.game_finished and self.solved_actions:
            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                if (self.ui_panel_x < mouse_pos[0] < self.ui_panel_x + self.ui_panel_width and
                    700 < mouse_pos[1] < SCREEN_HEIGHT):
                    
                    total_actions = len(self.solved_actions)
                    max_scroll = max(0, total_actions - self.max_actions_display)
                    
                    self.actions_scroll_y = max(0, min(max_scroll, 
                        self.actions_scroll_y - event.y))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.screen_manager.set_screen("menu")
            elif self.start_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.start_game()
            elif self.game_finished and self.solved_actions:
                if self.play_btn.is_point_inside(event.pos[0], event.pos[1]) and not self.is_animating:
                    self.start_animation()
                elif self.pause_btn.is_point_inside(event.pos[0], event.pos[1]):
                    self.pause_animation()
                elif self.reset_btn.is_point_inside(event.pos[0], event.pos[1]):
                    self.reset_animation()