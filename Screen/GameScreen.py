import pygame
import time
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
        self.Game = None
        self.is_playing = False
        self.game_step = 0
        self.game_finished = False
        self.actions = []
        self.wumpus_actions = []
        self.point = 0

        self.current_action = ""
        self.last_step_ms = 0
        self.step_delay_ms = 350

        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2

        self.slider_list = [
            {"label": "Map Size:", "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12), "label_pos": (self.ui_panel_x + 20, 140)},
            {"label": "Pit Density:", "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5), "label_pos": (self.ui_panel_x + 20, 220)},
            {"label": "Number of Wumpus:", "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5), "label_pos": (self.ui_panel_x + 20, 300)}
        ]

        button_width = self.ui_panel_width - 40
        self.start_btn = Button("Start", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.stop_btn = Button("Stop", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_RED, Color.WHITE, "body", "center")
        self.back_btn = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 550, Color.DARK_RED, Color.WHITE, "body", "center")

        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)

        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.ui_panel_x + 20, 420, "left", "body")

        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

    # ---------- render helpers ----------
    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_ui_panel_background(self, surface):
        panel_surface = pygame.Surface((self.ui_panel_width, SCREEN_HEIGHT))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(150)
        surface.blit(panel_surface, (self.ui_panel_x, 0))

    # ---------- main draw ----------
    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_ui_panel_background(surface)
        self.title.draw(surface)

        for item in self.slider_list:
            label = Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body")
            label.draw(surface)
            item["slider"].draw(surface)

        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        if self.is_playing:
            self.stop_btn.draw(surface)
        else:
            self.start_btn.draw(surface)
        self.back_btn.draw(surface)

        self.draw_game_map(surface)

    # ---------- game control ----------
    def start_game(self):
        size = int(self.slider_list[0]["slider"].value)
        pit = self.slider_list[1]["slider"].value
        wumpus = int(self.slider_list[2]["slider"].value)
        hard = self.toggle.value
        print("Game configuration: ", size, pit, wumpus, hard)
        self.Game = Game(size, pit, wumpus, hard)

        self.is_playing = True
        self.game_finished = False
        self.game_step = 0
        self.current_action = ""
        self.actions = []
        self.point = 0
        self.last_step_ms = pygame.time.get_ticks()

        self.solve_game()

        # reset agent to start if available
        if hasattr(self.Game.agent, "start_pos"):
            r, c = self.Game.agent.start_pos
            self.Game.agent.row, self.Game.agent.col = r, c

    def stop_game(self):
        self.is_playing = False
        self.game_finished = True
        self.current_action = ""

    def solve_game(self):
        if self.Game:
            try:
                self.point, self.actions, self.wumpus_actions = self.Game.play()
            except Exception as e:
                print("Game.play() error:", e)
                self.point, self.actions, self.wumpus_actions = 0, [], []

        print("Game score: ", self.point)
        print("Game actions: ", self.actions)
        print("Wumpus actions: ", self.wumpus_actions)

    def apply_visual_action(self, action):
        print("Applying action: ", action)

    # ---------- update loop ----------
    def update(self):
        if not self.is_playing:
            for item in self.slider_list:
                item["slider"].update()
            self.toggle.update()
            return

        now = pygame.time.get_ticks()
        if self.is_playing and self.actions and (now - self.last_step_ms >= self.step_delay_ms):
            self.last_step_ms = now

            action = self.actions[self.game_step]
            self.current_action = str(action)
            # apply current action to agent so it visibly moves
            try:
                self.apply_visual_action(action)
            except Exception as e:
                print("apply_visual_action error:", e)

            self.game_step += 1
            if self.game_step >= len(self.actions):
                self.is_playing = False
                self.game_finished = True
                self.current_action = "Done"

    # ---------- map draw ----------
    def draw_game_map(self, surface):
        if not self.Game or not self.Game.map:
            return
        self.Game.map.draw(surface)
        self.Game.agent.draw(surface)

    # ---------- input ----------
    def handle_event(self, event):
        if not self.is_playing:
            for item in self.slider_list:
                item["slider"].handle_event(event)
            self.toggle.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.stop_game()
                self.screen_manager.set_screen("menu")
            elif self.start_btn.is_point_inside(event.pos[0], event.pos[1]) and not self.is_playing:
                self.start_game()
            elif self.stop_btn.is_point_inside(event.pos[0], event.pos[1]) and self.is_playing:
                self.stop_game()
