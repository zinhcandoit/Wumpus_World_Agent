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
        self.is_playing = False

        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width  
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2

        # Slider list kèm label
        self.slider_list = [
            {
                "label": "Map Size:",
                "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12),
                "label_pos": (self.ui_panel_x + 20, 140)
            }, 
            {
                "label": "Pit Density:",
                "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5),
                "label_pos": (self.ui_panel_x + 20, 220)
            }, 
            {
                "label": "Number of Wumpus:",
                "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5),
                "label_pos": (self.ui_panel_x + 20, 300)
            }, 
        ]

        # Buttons
        button_width = self.ui_panel_width - 40
        self.start_btn = Button("Start", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.back_btn = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 550, Color.DARK_RED, Color.WHITE, "body", "center")

        self.button_list = [
            self.start_btn,
            self.back_btn
        ]

        # Toggle
        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)

        # Title
        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        
        # Background
        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

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

        # Slider + label
        for item in self.slider_list:
            label = Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body")
            label.draw(surface)
            item["slider"].draw(surface)

        # Toggle
        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        # Buttons
        for button in self.button_list:
            button.draw(surface)

        # Vẽ map game nếu đang chơi
        if self.is_playing and self.Game:
            self.draw_game_map(surface)

    def draw_game_map(self, surface):
        if self.Game:
            pass

    def update(self):
        if self.is_playing and self.Game:
            self.step_game()

        for item in self.slider_list:
            item["slider"].update()
        self.toggle.update()

    def step_game(self):
        agent = self.Game.agent
        agent.percepts = self.Game.map.get_percepts_for_agent(agent)
        agent.get_KB_from_percepts()
        action = agent.choose_action()
        self.Game.actions.append(action)
        self.Game.update_score()

        if action == "climb out":
            print("Agent climbed out!")
            self.is_playing = False
            return

        flag = self.Game.map.update_map(action, agent)
        print(f"Step {len(self.Game.actions)}: {action}")

        if flag is False:
            self.Game.actions.append("die")
            self.Game.update_score()
            print("Agent died!")
            self.is_playing = False
            return

        if len(self.Game.actions) > 20:
            print("Too many actions, stopping the game.")
            self.is_playing = False

    def handle_event(self, event):
        for item in self.slider_list:
            item["slider"].handle_event(event)
        for button in self.button_list:
            button.handle_event(event)
        self.toggle.handle_event(event)
        self.hard_mode = self.toggle.value

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            if self.back_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.screen_manager.set_screen("menu")
            elif self.start_btn.is_point_inside(event.pos[0], event.pos[1]):
                size = int(self.slider_list[0]["slider"].value)
                pit = self.slider_list[1]["slider"].value
                wumpus = int(self.slider_list[2]["slider"].value)
                hard = self.toggle.value
                self.Game = Game(size, pit, wumpus, hard)
                self.is_playing = True
                print("Game configuration: ", size, pit, wumpus, hard)