import pygame

class Board: 
    def __init__(self, width, height, x, y, bg_color, border_color, border_width):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

    def update(self):
        pass
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, 
                            (self.x, self.y, self.width, self.height), 
                            self.border_width)

    def handle_event(self, event):
        pass