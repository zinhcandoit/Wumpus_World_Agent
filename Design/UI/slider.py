import pygame

class Slider:
    def __init__(self, x, y, w, h, value, min_val, max_val):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.dragging = False
        
        # Colors
        self.bg_color = (200, 200, 200)
        self.fill_color = (100, 150, 255)
        self.handle_color = (50, 50, 50)
        self.border_color = (100, 100, 100)
        
        # Handle properties
        self.handle_radius = h // 2
        self.handle_x = self._value_to_x()

    def _value_to_x(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.x + ratio * self.w

    def _x_to_value(self, x):
        x = max(self.x, min(self.x + self.w, x))
        ratio = (x - self.x) / self.w
        return self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.w, self.h), 2)
        fill_width = self.handle_x - self.x
        if fill_width > 0:
            pygame.draw.rect(surface, self.fill_color, 
                           (self.x, self.y, fill_width, self.h))
        handle_y = self.y + self.h // 2
        pygame.draw.circle(surface, self.handle_color, 
                         (int(self.handle_x), handle_y), self.handle_radius)
        pygame.draw.circle(surface, self.border_color, 
                         (int(self.handle_x), handle_y), self.handle_radius, 2)

    def update(self):
        if self.dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            self.value = self._x_to_value(mouse_x)
            self.handle_x = self._value_to_x()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  
                mouse_x, mouse_y = event.pos
                handle_y = self.y + self.h // 2
                distance = ((mouse_x - self.handle_x) ** 2 + 
                            (mouse_y - handle_y) ** 2) ** 0.5
                if distance <= self.handle_radius:
                    self.dragging = True
                elif (self.x <= mouse_x <= self.x + self.w and 
                    self.y <= mouse_y <= self.y + self.h):
                    self.value = self._x_to_value(mouse_x)
                    self.handle_x = self._value_to_x()
                    self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
