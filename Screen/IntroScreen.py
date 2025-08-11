from Screen.BaseScreen import Screen
from Design.UI.text import Text
from Design.ImageManager.Image import Image
from constant import *
import pygame

class IntroScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.title = Text("Hello Wumpus World!!", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 100, "center", "title")
        self.members = [
            Text("Thieu Quang Vinh - 23127143", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 300, "center", "sub_title"),
            Text("Luong Thanh Loc - 23127405", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 350, "center", "sub_title"),
            Text("Tran Hai Duc - 23127173", "Arial", Color.WHITE, SCREEN_WIDTH // 2, 400, "center", "sub_title"),
        ]
        self.instruction = Text("Press any key to start", "Arial", Color.YELLOW, 
                               SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, "center", "body")
        
        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        
        # Tạo overlay tối để chữ hiển thị rõ hơn
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(120)

    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_title(self, surface):
        self.title.draw(surface)

    def draw_members(self, surface):
        for member in self.members:
            member.draw(surface)

    def draw_instruction(self, surface):
        self.instruction.draw(surface)

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_title(surface)
        self.draw_members(surface)
        self.draw_instruction(surface)

    def update(self):
        pass

    def on_enter(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.screen_manager.set_screen("menu")