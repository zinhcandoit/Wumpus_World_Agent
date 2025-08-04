from Screen.BaseScreen import Screen
from constant import *
import pygame

class IntroScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.title = "INTRO"
        self.title_pos = (SCREEN_WIDTH // 2, 100)

    def draw_test(self, surface):
        pygame.draw.rect(surface, Color.BLUE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.SysFont("Arial", 48) 
        text_surface = font.render(self.title, True, Color.WHITE)        
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))        
        surface.blit(text_surface, text_rect)

    def draw(self, surface):
        self.draw_test(surface)

    def update(self):
        pass

    def on_enter(self):
        pass

    def handle_event(self, event):
        # có event click chuột hoặc nhấn nút thì next luôn
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.screen_manager.set_screen("menu")