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
        
        # Cấu hình game cơ bản
        self.map_size = 8
        self.pit_density = 0.2
        self.num_wumpus = 2
        self.hard_mode = False
        
        # Trạng thái game
        self.game = None
        self.game_ready = False
        self.game_result = None
        self.actions_list = []
        
        # Trạng thái animation
        self.is_playing = False
        self.is_paused = False
        self.current_step = 0
        self.last_update_time = 0
        self.animation_speed = 1000  # milliseconds per step
        
        # Vị trí và hướng của agent trong animation
        self.agent_pos = (0, 0)  # (row, col)
        self.agent_direction = "right"
        
        # Vị trí wumpus trong animation
        self.wumpus_movements = []
        self.initial_wumpus_pos = []
        self.current_wumpus_pos = []
        self.wumpus_alive = []
        
        self._setup_ui()
        self._load_images()

    def _setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Kích thước và vị trí panel
        self.panel_width = SCREEN_WIDTH // 4
        self.panel_x = SCREEN_WIDTH - self.panel_width
        self.panel_center_x = self.panel_x + self.panel_width // 2
        
        # Sliders cho cấu hình game
        self.sliders = [
            {"name": "Map Size:", "slider": Slider(self.panel_center_x, 145, 120, 20, 6, 4, 8), "pos": (self.panel_x + 20, 140)},
            {"name": "Pit Density:", "slider": Slider(self.panel_center_x, 225, 120, 20, 0.2, 0.1, 0.5), "pos": (self.panel_x + 20, 220)},
            {"name": "Wumpus Count:", "slider": Slider(self.panel_center_x, 305, 120, 20, 2, 1, 5), "pos": (self.panel_x + 20, 300)},
        ]
        
        # Buttons
        button_width = self.panel_width - 40
        self.start_button = Button("Start Game", "Arial", button_width, 40, self.panel_center_x, 440, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.back_button = Button("Back to Menu", "Arial", button_width, 40, self.panel_center_x, 490, Color.DARK_RED, Color.WHITE, "body", "center")
        
        # Animation controls
        self.play_button = Button("Play", "Arial", button_width, 30, self.panel_center_x, 540, Color.BLUE, Color.WHITE, "small", "center")
        self.pause_button = Button("Pause", "Arial", button_width//2 - 5, 30, self.panel_center_x - button_width//4, 580, Color.ORANGE, Color.WHITE, "small", "center")
        self.reset_button = Button("Reset", "Arial", button_width//2 - 5, 30, self.panel_center_x + button_width//4, 580, Color.GRAY, Color.WHITE, "small", "center")
        
        # Toggle và speed control
        self.hard_mode_toggle = Toggle(self.panel_x + self.panel_width - 60, 355, value=False)
        self.speed_slider = Slider(self.panel_center_x, 625, 120, 15, 1.0, 0.2, 3.0)
        
        # Text elements
        self.title_text = Text("Game Configuration", "Arial", Color.WHITE, self.panel_center_x, 50, "center", "sub_title")
        self.hard_mode_text = Text("Hard Mode", "Arial", Color.WHITE, self.panel_x + 20, 360, "left", "body")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.panel_x + 20, 390, "left", "body")
        self.speed_text = Text("Animation Speed:", "Arial", Color.WHITE, self.panel_x + 20, 620, "left", "small")

    def _load_images(self):
        """Tải và thiết lập các hình ảnh"""
        # Background
        self.background = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)
        
        # Game objects
        self.agent_img = Image("assets/agent.png")
        self.tile_img = Image("assets/tileset/tile.png")
        self.pit_img = Image("assets/pit.png")
        self.gold_img = Image("assets/gold.png")
        self.wumpus_img = Image("assets/wumpus 1.png")
        self.stench_img = Image("assets/stench.png")
        self.breeze_img = Image("assets/breeze.png")
        
        # Cache cho scaled images
        self.scaled_images = {}
        self.agent_rotated = {}

    def start_new_game(self):
        """Khởi tạo game mới với cấu hình hiện tại"""
        # Lấy giá trị từ UI
        size = int(self.sliders[0]["slider"].value)
        pit = self.sliders[1]["slider"].value
        wumpus = int(self.sliders[2]["slider"].value)
        hard = self.hard_mode_toggle.value
        
        print(f"Starting game: {size}x{size}, pit density: {pit}, wumpus: {wumpus}, hard mode: {hard}")
        
        # Reset trạng thái
        self.game_ready = False
        self.game_result = None
        self.actions_list = []
        self.stop_animation()
        
        # Tạo game mới
        self.game = Game(size, pit, wumpus, hard)
        self.agent_pos = (size - 1, 0)  # Vị trí bắt đầu (góc dưới trái)
        self.agent_direction = "right"
        
        # Lấy vị trí wumpus ban đầu
        self.initial_wumpus_pos = self._get_wumpus_positions()
        self.current_wumpus_pos = self.initial_wumpus_pos.copy()
        self.wumpus_alive = [True] * len(self.initial_wumpus_pos)
        
        # Chạy AI solver
        score, actions, wumpus_moves = self.game.play()
        
        # Lưu kết quả
        self.game_result = score
        self.actions_list = actions or []
        self.wumpus_movements = wumpus_moves or []
        self.game_ready = True
        
        print(f"Game completed - Score: {score}, Actions: {len(self.actions_list)}")

    def _get_wumpus_positions(self):
        """Tìm tất cả vị trí wumpus trên map"""
        if not self.game or not hasattr(self.game, "map"):
            return []
        
        positions = []
        for r in range(len(self.game.map.grid)):
            for c in range(len(self.game.map.grid[0])):
                if 'wumpus' in self.game.map.grid[r][c]:
                    positions.append((r, c))
        return positions

    def start_animation(self):
        """Bắt đầu phát animation"""
        if self.game_ready and self.actions_list:
            self.is_playing = True
            self.is_paused = False
            self.last_update_time = pygame.time.get_ticks()
            if self.current_step == 0:
                self._reset_to_start_position()

    def pause_animation(self):
        """Tạm dừng/tiếp tục animation"""
        if self.is_playing:
            self.is_paused = not self.is_paused
            if not self.is_paused:
                self.last_update_time = pygame.time.get_ticks()

    def stop_animation(self):
        """Dừng và reset animation"""
        self.is_playing = False
        self.is_paused = False
        self.current_step = 0
        if self.game:
            self._reset_to_start_position()

    def _reset_to_start_position(self):
        """Reset về vị trí ban đầu"""
        if not self.game:
            return
            
        size = len(self.game.map.grid)
        self.agent_pos = (size - 1, 0)
        self.agent_direction = "right"
        self.current_wumpus_pos = self.initial_wumpus_pos.copy()
        self.wumpus_alive = [True] * len(self.initial_wumpus_pos)

    def update(self):
        """Cập nhật trạng thái của screen"""
        # Cập nhật UI controls
        for slider_info in self.sliders:
            slider_info["slider"].update()
        
        self.hard_mode_toggle.update()
        
        if self.game_ready:
            self.speed_slider.update()
        
        # Cập nhật animation
        self._update_animation()

    def _update_animation(self):
        """Cập nhật animation nếu đang chạy"""
        if not self.is_playing or self.is_paused:
            return
        
        current_time = pygame.time.get_ticks()
        step_duration = max(200, int(self.animation_speed / self.speed_slider.value))
        
        if current_time - self.last_update_time >= step_duration:
            if self.current_step < len(self.actions_list):
                self._execute_animation_step()
                self._update_wumpus_for_step()
                self.current_step += 1
                self.last_update_time = current_time
            else:
                self.is_playing = False

    def _execute_animation_step(self):
        """Thực hiện một bước animation"""
        if self.current_step >= len(self.actions_list):
            return
        
        action = self.actions_list[self.current_step].lower().strip()
        row, col = self.agent_pos
        
        if action == "move":
            # Di chuyển theo hướng hiện tại
            if self.agent_direction == "up":
                self.agent_pos = (max(0, row - 1), col)
            elif self.agent_direction == "down":
                self.agent_pos = (min(len(self.game.map.grid) - 1, row + 1), col)
            elif self.agent_direction == "left":
                self.agent_pos = (row, max(0, col - 1))
            elif self.agent_direction == "right":
                self.agent_pos = (row, min(len(self.game.map.grid[0]) - 1, col + 1))
        
        elif "turn left" in action:
            # Quay trái
            turn_left = {"right": "up", "up": "left", "left": "down", "down": "right"}
            self.agent_direction = turn_left.get(self.agent_direction, self.agent_direction)
        
        elif "turn right" in action:
            # Quay phải
            turn_right = {"right": "down", "down": "left", "left": "up", "up": "right"}
            self.agent_direction = turn_right.get(self.agent_direction, self.agent_direction)

    def _update_wumpus_for_step(self):
        """Cập nhật vị trí wumpus cho bước hiện tại"""
        if not self.wumpus_movements or self.current_step >= len(self.wumpus_movements[0]):
            return
        
        for wumpus_idx in range(len(self.current_wumpus_pos)):
            if wumpus_idx >= len(self.wumpus_movements):
                continue
                
            if self.current_step >= len(self.wumpus_movements[wumpus_idx]):
                continue
            
            action = self.wumpus_movements[wumpus_idx][self.current_step]
            
            if action == 'dead':
                self.wumpus_alive[wumpus_idx] = False
            elif action == 'stay' or not self.wumpus_alive[wumpus_idx]:
                continue
            else:
                # Di chuyển wumpus
                self._move_wumpus(wumpus_idx, action)

    def _move_wumpus(self, wumpus_idx, direction):
        """Di chuyển wumpus theo hướng chỉ định"""
        if self.current_wumpus_pos[wumpus_idx] is None:
            return
            
        row, col = self.current_wumpus_pos[wumpus_idx]
        max_row = len(self.game.map.grid) - 1
        max_col = len(self.game.map.grid[0]) - 1
        
        if direction == 'N':
            row = max(0, row - 1)
        elif direction == 'S':
            row = min(max_row, row + 1)
        elif direction == 'W':
            col = max(0, col - 1)
        elif direction == 'E':
            col = min(max_col, col + 1)
        
        self.current_wumpus_pos[wumpus_idx] = (row, col)

    def draw(self, surface):
        """Vẽ toàn bộ screen"""
        self._draw_background(surface)
        self._draw_ui_panel(surface)
        
        if self.game:
            self._draw_game_map(surface)

    def _draw_background(self, surface):
        """Vẽ background"""
        self.background.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def _draw_ui_panel(self, surface):
        """Vẽ panel UI bên phải"""
        # Background panel
        panel_surface = pygame.Surface((self.panel_width, SCREEN_HEIGHT))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(150)
        surface.blit(panel_surface, (self.panel_x, 0))
        
        # Title
        self.title_text.draw(surface)
        
        # Sliders
        for slider_info in self.sliders:
            Text(slider_info["name"], "Arial", Color.WHITE, slider_info["pos"][0], slider_info["pos"][1], "left", "body").draw(surface)
            slider_info["slider"].draw(surface)
        
        # Hard mode toggle
        self.hard_mode_text.draw(surface)
        self.hard_mode_toggle.draw(surface)
        
        # Buttons
        self.start_button.draw(surface)
        self.back_button.draw(surface)
        
        # Animation controls
        if self.game_ready and self.actions_list:
            if not self.is_playing:
                self.play_button.draw(surface)
            
            self.pause_button.draw(surface)
            self.reset_button.draw(surface)
            
            # Speed control
            self.speed_text.draw(surface)
            self.speed_slider.draw(surface)
            
            # Progress
            progress = f"Step: {min(self.current_step + 1, len(self.actions_list))}/{len(self.actions_list)}"
            progress_text = Text(progress, "Arial", Color.CYAN, self.panel_x + 20, 675, "left", "small")
            progress_text.draw(surface)

    def _draw_game_map(self, surface):
        """Vẽ bản đồ game"""
        if not hasattr(self.game, "map") or not self.game.map.grid:
            return

        grid = self.game.map.grid
        rows, cols = len(grid), len(grid[0])
        
        # Tính toán kích thước ô
        map_width = SCREEN_WIDTH - self.panel_width
        map_height = SCREEN_HEIGHT
        margin = 20
        
        cell_size = min(
            (map_width - 2 * margin) // cols,
            (map_height - 2 * margin) // rows
        )
        
        start_x = margin
        start_y = (map_height - rows * cell_size) // 2
        
        # Vẽ lưới và ô
        self._draw_map_content(surface, start_x, start_y, rows, cols, cell_size, grid)

    def _draw_map_content(self, surface, start_x, start_y, rows, cols, cell_size, grid):
        """Vẽ nội dung bản đồ"""
        # Lấy scaled images
        images = self._get_scaled_images(cell_size)
        
        # Vẽ từng ô
        for r in range(rows):
            for c in range(cols):
                x = start_x + c * cell_size
                y = start_y + r * cell_size
                
                # Vẽ tile nền
                surface.blit(images["tile"], (x, y))
                
                # Vẽ các object (trừ agent và wumpus)
                for obj in grid[r][c]:
                    if obj in images and obj not in ["agent", "wumpus"]:
                        surface.blit(images[obj], (x, y))
        
        # Vẽ wumpus
        self._draw_wumpuses(surface, start_x, start_y, cell_size, images, grid)
        
        # Vẽ agent
        self._draw_agent(surface, start_x, start_y, cell_size, images, grid)

    def _draw_wumpuses(self, surface, start_x, start_y, cell_size, images, grid):
        """Vẽ các wumpus"""
        if self.game_ready and self.is_playing:
            # Vẽ wumpus ở vị trí animation
            for idx, pos in enumerate(self.current_wumpus_pos):
                if pos and self.wumpus_alive[idx]:
                    row, col = pos
                    x = start_x + col * cell_size
                    y = start_y + row * cell_size
                    surface.blit(images["wumpus"], (x, y))
        else:
            # Vẽ wumpus ở vị trí ban đầu
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if "wumpus" in grid[r][c]:
                        x = start_x + c * cell_size
                        y = start_y + r * cell_size
                        surface.blit(images["wumpus"], (x, y))

    def _draw_agent(self, surface, start_x, start_y, cell_size, images, grid):
        """Vẽ agent"""
        if self.game_ready and self.is_playing:
            # Vẽ agent ở vị trí animation với hướng đúng
            row, col = self.agent_pos
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            agent_img = self._get_rotated_agent_image(cell_size)
            surface.blit(agent_img, (x, y))
        else:
            # Vẽ agent ở vị trí ban đầu
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if "agent" in grid[r][c]:
                        x = start_x + c * cell_size
                        y = start_y + r * cell_size
                        surface.blit(images["agent"], (x, y))

    def _get_scaled_images(self, size):
        """Lấy images đã scale theo kích thước"""
        if size not in self.scaled_images:
            self.scaled_images[size] = {
                "tile": pygame.transform.smoothscale(self.tile_img.image, (size, size)),
                "agent": pygame.transform.smoothscale(self.agent_img.image, (size, size)),
                "pit": pygame.transform.smoothscale(self.pit_img.image, (size, size)),
                "gold": pygame.transform.smoothscale(self.gold_img.image, (size, size)),
                "wumpus": pygame.transform.smoothscale(self.wumpus_img.image, (size, size)),
                "stench": pygame.transform.smoothscale(self.stench_img.image, (size, size)),
                "breeze": pygame.transform.smoothscale(self.breeze_img.image, (size, size)),
            }
        return self.scaled_images[size]

    def _get_rotated_agent_image(self, size):
        """Lấy hình agent đã xoay theo hướng"""
        if size not in self.agent_rotated:
            base_img = pygame.transform.smoothscale(self.agent_img.image, (size, size))
            self.agent_rotated[size] = {
                "right": base_img,
                "left": pygame.transform.flip(base_img, True, False),
                "up": pygame.transform.rotate(base_img, 90),
                "down": pygame.transform.rotate(base_img, -90)
            }
        return self.agent_rotated[size][self.agent_direction]

    def handle_event(self, event):
        """Xử lý sự kiện"""
        # Cập nhật UI controls khi game chưa bắt đầu
        if not self.game or self.game_ready:
            for slider_info in self.sliders:
                slider_info["slider"].handle_event(event)
            self.hard_mode_toggle.handle_event(event)
        
        # Speed slider luôn có thể điều chỉnh
        if self.game_ready:
            self.speed_slider.handle_event(event)

        # Xử lý click buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            
            if self.back_button.is_point_inside(x, y):
                self.screen_manager.set_screen("menu")
            elif self.start_button.is_point_inside(x, y):
                self.start_new_game()
            elif self.game_ready and self.actions_list:
                if self.play_button.is_point_inside(x, y) and not self.is_playing:
                    self.start_animation()
                elif self.pause_button.is_point_inside(x, y):
                    self.pause_animation()
                elif self.reset_button.is_point_inside(x, y):
                    self.stop_animation()