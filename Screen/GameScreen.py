import pygame
from Screen.BaseScreen import Screen
from Design.UI.text import Text
from Design.UI.slider import Slider
from Design.UI.button import Button
from Design.UI.board import Board
from Design.UI.toggle import Toggle
from Design.ImageManager.Image import Image
from constant import *

class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.map_size = 8
        self.pit_density = 0.2
        self.num_wumpus = 2
        self.hard_mode = False

        self.side_board = Board(200, 600, 0, 0, Color.DARK_GREEN, Color.DARK_GREEN, 0) 

        # Slider list kèm label
        self.slider_list = [
            {
                "label": "Map Size:",
                "slider": Slider(0, 0, 200, 20, 8, 4, 12)
            }, 
            {
                "label": "Pit Density:",
                "slider": Slider(0, 0, 200, 20, 8, 0.1, 0.5)
            }, 
            {
                "label": "Number of Wumpus:",
                "slider": Slider(0, 0, 200, 20, 2, 1, 5)
            }, 
        ]

        # Buttons
        self.save_config_btn = Button("Save configuration", "Arial", 200, 50, SCREEN_WIDTH // 2, 400, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.start_btn = Button("Start", "Arial", 200, 50, SCREEN_WIDTH // 2, 600, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.back_btn = Button("Back to menu", "Arial", 200, 50, SCREEN_WIDTH // 2, 700, Color.DARK_RED, Color.WHITE, "body", "center")

        self.button_list = [
            self.save_config_btn,
            self.start_btn,
            self.back_btn
        ]

        # Toggle
        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, SCREEN_WIDTH // 2 - 150, 500, "left", "body")
        self.toggle = Toggle(SCREEN_WIDTH // 2 + 50, 495, value=False)

        self.title = Text("GAME PLAY", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 150, "center", "title")
        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

        # Căn vị trí slider
        self._arrange_ui()

    def _arrange_ui(self):
        start_y = 220
        spacing = 60
        center_x = SCREEN_WIDTH // 2

        for i, item in enumerate(self.slider_list):
            slider = item["slider"]
            slider.x = center_x
            slider.y = start_y + i * spacing
            item["label_pos"] = (center_x - slider.w // 2 - 150, slider.y + 5)  # label bên trái

    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_title(self, surface):
        self.title.draw(surface)

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_title(surface)

        # Vẽ slider + label
        for item in self.slider_list:
            label = Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body")
            label.draw(surface)
            item["slider"].draw(surface)

        # Vẽ toggle
        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        # Vẽ buttons
        for button in self.button_list:
            button.draw(surface)

    def update(self):
        for item in self.slider_list:
            item["slider"].update()
        self.toggle.update()

    def on_enter(self):
        pass

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
            elif self.save_config_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.map_size = self.slider_list[0]["slider"].value
                self.pit_density = self.slider_list[1]["slider"].value
                self.num_wumpus = self.slider_list[2]["slider"].value
                print(f"Saved config: map_size={self.map_size}, pit_density={self.pit_density}, num_wumpus={self.num_wumpus}, hard_mode={self.hard_mode}")
            # elif self.start_btn.is_point_inside(event.pos[0], event.pos[1]):
            #     self.game.map = Map(self.map_size, self.pit_density, self.num_wumpus, hard=self.hard_mode)
            #     self.game.start_algo()
