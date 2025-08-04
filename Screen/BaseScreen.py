from constant import *

class ScreenManager:
    def __init__(self):
        self.screens = {}
        self.current_screen = None
        
    def add_screen(self, name, screen):
        self.screens[name] = screen
        
    def set_screen(self, name):
        if name in self.screens:
            self.current_screen = self.screens[name]
            if hasattr(self.current_screen, 'on_enter'):
                self.current_screen.on_enter()
                
    def update(self):
        if self.current_screen:
            return self.current_screen.update()
        return True
        
    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)


class Screen:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

    def update(self):
        pass
        
    def draw(self, surface):
        surface.fill(Color.BLACK)
        
    def handle_event(self, event):
        pass
        
    def on_enter(self):
        pass