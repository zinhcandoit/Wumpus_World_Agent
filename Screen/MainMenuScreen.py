from Screen.BaseScreen import Screen
from Design.UI.button import Button
from Design.UI.board import Board
from Design.UI.text import Text
from Design.ImageManager.Image import Image
from constant import *
import pygame
import sys

class MainMenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.title = Text("WUMPUS WORLD", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 150, "center", "title")

        button_y_start = SCREEN_HEIGHT // 2 - 30
        self.play_btn = Button("Play", "Arial", 200, 50, SCREEN_WIDTH // 2, button_y_start, Color.DARK_GREEN, Color.WHITE, "body", "center")
        
        self.quit_btn = Button("Exit", "Arial", 200, 50, SCREEN_WIDTH // 2,  button_y_start + 70, Color.DARK_RED, Color.WHITE, "body", "center")

        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

    def draw(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))
        self.title.draw(surface)
        self.play_btn.draw(surface)
        self.quit_btn.draw(surface)

    def update(self):
        self.play_btn.update()
        self.quit_btn.update()

    def on_enter(self):
        pass

    def handle_event(self, event):
        self.play_btn.handle_event(event)
        self.quit_btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            if self.play_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.screen_manager.set_screen("game")
            elif self.quit_btn.is_point_inside(event.pos[0], event.pos[1]):
                pygame.quit()
                sys.exit()