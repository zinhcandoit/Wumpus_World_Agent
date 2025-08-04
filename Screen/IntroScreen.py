from Screen.BaseScreen import Screen
from Design.UI.text import Text
from constant import *
import pygame

class IntroScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.title = Text("Hello Wumpus World!!", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 100, "center", "title")

    def draw(self, surface):
        self.title.draw(surface)

    def update(self):
        pass

    def on_enter(self):
        pass

    def handle_event(self, event):
        # có event click chuột hoặc nhấn nút thì next luôn
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.screen_manager.set_screen("menu")