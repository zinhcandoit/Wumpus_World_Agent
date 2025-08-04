from enum import Enum
from constant import *
import pygame
from Design.UI.text import Text

class ButtonState(Enum):
    IDLE = "idle"
    HOVERED = "hovered"
    CLICKED = "clicked"

class Button:
    def __init__(self, text, font, width, height, x, y, bg_color, text_color, type="body", relative_pos="top_left"):
        self.width = width
        self.height = height
        self.relative_pos = relative_pos
        self.color = bg_color
        self.original_color = bg_color
        self.is_clicked = False
        self.is_hovered = False
        self.state = ButtonState.IDLE
        
        self.x, self.y = self.calculate_button_position(x, y, width, height, relative_pos)
        
        self.text = Text(text, font, text_color, x, y, relative_pos, type)
        self.update_text_position()
    
    def calculate_button_position(self, x, y, width, height, relative_pos):
        if relative_pos == "center":
            return (x - width // 2, y - height // 2)
        elif relative_pos == "top_center":
            return (x - width // 2, y)
        elif relative_pos == "bottom_center":
            return (x - width // 2, y - height)
        elif relative_pos == "center_left":
            return (x, y - height // 2)
        elif relative_pos == "center_right":
            return (x - width, y - height // 2)
        elif relative_pos == "top_right":
            return (x - width, y)
        elif relative_pos == "bottom_left":
            return (x, y - height)
        elif relative_pos == "bottom_right":
            return (x - width, y - height)
        else:  # top_left (default)
            return (x, y)
    
    def update_text_position(self):
        # đặt vị trí text ở trung tâm trong button
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        self.text.set_position(center_x, center_y)
        self.text.set_relative_pos("center")
    
    def set_position(self, x, y):
        self.x, self.y = self.calculate_button_position(x, y, self.width, self.height, self.relative_pos)
        self.update_text_position()
    
    def is_point_inside(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def handle_mouse_move(self, mouse_x, mouse_y):
        self.is_hovered = self.is_point_inside(mouse_x, mouse_y)
        self.update_state()
    
    def handle_mouse_click(self, mouse_x, mouse_y):
        if self.is_point_inside(mouse_x, mouse_y):
            self.is_clicked = True
            self.update_state()
            return True
        return False
    
    def handle_mouse_release(self):
        self.is_clicked = False
        self.update_state()
    
    def get_state(self):
        if self.is_clicked:
            return ButtonState.CLICKED
        elif self.is_hovered:
            return ButtonState.HOVERED
        else:
            return ButtonState.IDLE

    def update_state(self):
        self.state = self.get_state()
        self.update_appearance()
    
    def update_appearance(self):
        if self.state == ButtonState.CLICKED:
            self.color = self.darken_color(self.original_color)
        elif self.state == ButtonState.HOVERED:
            self.color = self.lighten_color(self.original_color)
        else:
            self.color = self.original_color
    
    def darken_color(self, color):
        # làm tối màu khi nhấn
        if isinstance(color, tuple) and len(color) == 3:
            return tuple(max(0, c - 30) for c in color)
        return color
    
    def lighten_color(self, color):
        # làm sáng màu khi hover
        if isinstance(color, tuple) and len(color) == 3:
            return tuple(min(255, c + 30) for c in color)
        return color
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=8)
        self.text.draw(surface)
    
    def update(self):
        self.text.update()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_move(event.pos[0], event.pos[1])
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  
                self.handle_mouse_click(event.pos[0], event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: 
                self.handle_mouse_release()