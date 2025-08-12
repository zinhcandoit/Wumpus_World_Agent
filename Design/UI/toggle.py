import pygame
from constant import Color

class Toggle:
    def __init__(self, x, y, value=False, w=50, h=25):
        self.x = x
        self.y = y
        self.value = value  # True = Hard, False = Easy
        self.w = w
        self.h = h
        self.handle_radius = h // 2 - 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surface):
        # Màu nền: đỏ nếu Hard, xanh nếu Easy
        bg_color = Color.DARK_RED if self.value else Color.DARK_GREEN
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.h // 2)

        # Vị trí nút tròn
        if self.value:
            handle_x = self.x + self.w - self.handle_radius - 4
        else:
            handle_x = self.x + self.handle_radius + 2

        handle_y = self.y + self.h // 2
        pygame.draw.circle(surface, Color.WHITE, (handle_x, handle_y), self.handle_radius)

    def update(self):
        pass  # Toggle không có animation phức tạp

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value
