from Screen.BaseScreen import Screen
from Design.UI.button import Button
from constant import *
import pygame
import sys

class MainMenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.play_btn = Button(
            "Play", 
            "Arial", 
            DEFAULT_BUTTON_WIDTH, 
            DEFAULT_BUTTON_HEIGHT, 
            SCREEN_WIDTH // 2,  
            SCREEN_HEIGHT // 2 - 50, 
            Color.RED, 
            Color.WHITE, 
            "body", 
            "center"  
        )
        
        self.quit_btn = Button(
            "Quit", 
            "Arial", 
            DEFAULT_BUTTON_WIDTH, 
            DEFAULT_BUTTON_HEIGHT, 
            SCREEN_WIDTH // 2,  
            SCREEN_HEIGHT // 2 + 50, 
            Color.BLUE, 
            Color.WHITE, 
            "body", 
            "center" 
        )

    def draw(self, surface):
        surface.fill(Color.BLACK)        
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
    