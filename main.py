import pygame
import sys
from constant import *
from Screen.BaseScreen import ScreenManager
from Screen.IntroScreen import IntroScreen
from Screen.MainMenuScreen import MainMenuScreen

class GameManager:
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)
        return cls._instance

    def create_window(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Wumpus World Agent")
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def create_all_screens(self):
        self.screen_manager.add_screen('intro', IntroScreen(self.screen_manager))
        self.screen_manager.add_screen('menu', MainMenuScreen(self.screen_manager))

    def __init__(self):
        # Chỉ init lần đầu
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Create window
        self.create_window()        
        
        # Initialize screen manager
        self.screen_manager = ScreenManager()

        # Create all screens
        self.create_all_screens()

        # Start with intro screen
        self.screen_manager.set_screen('intro')

        # Mark as initialized
        self._initialized = True

    def run(self):
        running = True
        while running:
            # RECEIVE EVENT
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if self.screen_manager.current_screen:
                        self.screen_manager.current_screen.handle_event(event)

            # UPDATE 
            self.screen_manager.update()  

            # DRAW ALL IN THE BACK BUFFER
            self.buffer.fill(Color.BLACK)
            self.screen_manager.draw(self.buffer)
            self.screen.blit(self.buffer, (0, 0))
            
            # FLIP TO THE FRONT BUFFER
            pygame.display.flip()
            
            # WAITING TIME TILL NEXT FRAME
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    GameManager().run()



