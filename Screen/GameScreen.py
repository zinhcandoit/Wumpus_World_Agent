
import pygame
from Screen.BaseScreen import Screen
from Design.UI.text import Text
from Design.UI.slider import Slider
from Design.UI.button import Button
from Design.UI.toggle import Toggle
from Design.ImageManager.Image import Image
from Development.gameState import Game
from constant import *

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

        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2

        self.slider_list = [
            {"label": "Map Size:", "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12), "label_pos": (self.ui_panel_x + 20, 140)},
            {"label": "Pit Density:", "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5), "label_pos": (self.ui_panel_x + 20, 220)},
            {"label": "Number of Wumpus:", "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5), "label_pos": (self.ui_panel_x + 20, 300)},
        ]

        button_width = self.ui_panel_width - 40
        self.start_btn = Button("Start", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.back_btn  = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 550, Color.DARK_RED, Color.WHITE, "body", "center")

        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)

        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.ui_panel_x + 20, 420, "left", "body")

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

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_ui_panel_background(surface)
        self.draw_title(surface)

        for item in self.slider_list:
            Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body").draw(surface)
            item["slider"].draw(surface)

        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        if self.game_finished and self.solved_point is not None:
            msg = f"Solved: {len(self.solved_actions)} actions, Point: {self.solved_point}"
        else:
            msg = "Ready to start"
        self.status_text.text = msg
        self.status_text.draw(surface)

        self.start_btn.draw(surface)
        self.back_btn.draw(surface)

        if self.Game:
            self.draw_game_map(surface)

    def start_game(self):
        size = int(self.slider_list[0]["slider"].value)
        pit = self.slider_list[1]["slider"].value
        wumpus = int(self.slider_list[2]["slider"].value)
        hard = self.toggle.value

        print("Game configuration:", size, pit, wumpus, hard)

        # Khởi tạo game và gọi solver đồng bộ
        self.Game = Game(size, pit, wumpus, hard)

        point, actions = self.Game.play()

        # Lưu và in ra
        self.solved_point = point
        self.solved_actions = actions or []
        self.game_finished = True

        print("Point:", point)
        print("Actions:", self.solved_actions)

    def update(self):
        for item in self.slider_list:
            item["slider"].update()
        self.toggle.update()

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
        agent_img  = _scale(self.agent_image)

        token_to_img = {
            "gold": gold_img,
            "wumpus": wumpus_img,
            "pit": pit_img,
            "stench": stench_img,
            "breeze": breeze_img,
            "agent": agent_img,
        }

        # Vẽ lưới
        grid_color = (40, 40, 40)
        for r in range(rows + 1):
            y = origin_y + r * cell_size
            pygame.draw.line(surface, grid_color, (origin_x, y), (origin_x + cols * cell_size, y), 1)
        for c in range(cols + 1):
            x = origin_x + c * cell_size
            pygame.draw.line(surface, grid_color, (x, origin_y), (x, origin_y + rows * cell_size), 1)

        for r in range(rows):
            for c in range(cols):
                x = origin_x + c * cell_size
                y = origin_y + r * cell_size
                surface.blit(tile_img, (x, y))

                for tok in grid[r][c]:
                    img = token_to_img.get(tok)
                    if img:
                        surface.blit(img, (x, y))


    def handle_event(self, event):
        # Không dùng user event tùy biến, không dùng thread
        if not self.Game or self.game_finished:
            for item in self.slider_list:
                item["slider"].handle_event(event)
            self.toggle.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.screen_manager.set_screen("menu")
            elif self.start_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.start_game()

