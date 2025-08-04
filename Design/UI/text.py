import pygame

class Text:
    def __init__(self, text, font, color, x, y, relative_pos="top_left", type="body"):
        self.text = text
        self.font_name = font
        self.color = color
        self.x = x
        self.y = y
        self.relative_pos = relative_pos
        self.type = type
        self.size = self.set_size_by_type()
        self.font = pygame.font.SysFont(self.font_name, self.size)
        
        self.text_surface = None
        self.text_rect = None
        self.update_text_surface()

    def update_text_surface(self):
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.update_position()

    def update_position(self):
        if self.relative_pos == "center":
            self.text_rect.center = (self.x, self.y)
        elif self.relative_pos == "top_left":
            self.text_rect.topleft = (self.x, self.y)
        elif self.relative_pos == "top_right":
            self.text_rect.topright = (self.x, self.y)
        elif self.relative_pos == "top_center":
            self.text_rect.midtop = (self.x, self.y)
        elif self.relative_pos == "bottom_left":
            self.text_rect.bottomleft = (self.x, self.y)
        elif self.relative_pos == "bottom_right":
            self.text_rect.bottomright = (self.x, self.y)
        elif self.relative_pos == "bottom_center":
            self.text_rect.midbottom = (self.x, self.y)
        elif self.relative_pos == "center_left":
            self.text_rect.midleft = (self.x, self.y)
        elif self.relative_pos == "center_right":
            self.text_rect.midright = (self.x, self.y)
        else:
            # Mặc định là top_left
            self.text_rect.topleft = (self.x, self.y)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.update_position()

    def set_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self.update_text_surface()

    def set_color(self, new_color):
        if self.color != new_color:
            self.color = new_color
            self.update_text_surface()

    def set_relative_pos(self, new_relative_pos):
        self.relative_pos = new_relative_pos
        self.update_position()

    def update(self):
        pass

    def set_size_by_type(self):
        size_map = {
            "title": 48,
            "sub_title": 24,
            "body": 16,
            "small": 12,
            "large": 32
        }
        return size_map.get(self.type, 16)

    def draw(self, surface):
        if self.text_surface and self.text_rect:
            surface.blit(self.text_surface, self.text_rect)

    def get_rect(self):
        return self.text_rect.copy() if self.text_rect else None

    def get_size(self):
        if self.text_rect:
            return self.text_rect.size
        return (0, 0)

    def handle_event(self, event):
        pass

