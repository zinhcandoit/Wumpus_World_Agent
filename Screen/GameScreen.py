import pygame
import threading
import time
from Screen.BaseScreen import Screen
from Design.UI.text import Text
from Design.UI.slider import Slider
from Design.UI.button import Button
from Design.UI.toggle import Toggle
from Design.ImageManager.Image import Image
from Development.gameState import Game
from constant import *

GAME_STEP_EVENT = pygame.USEREVENT + 1
GAME_END_EVENT = pygame.USEREVENT + 2

class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.Game = None
        self.is_playing = False
        self.game_thread = None
        self.current_action = ""
        self.game_step = 0
        self.game_finished = False

        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width  
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2

        self.slider_list = [
            {"label": "Map Size:", "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12), "label_pos": (self.ui_panel_x + 20, 140)}, 
            {"label": "Pit Density:", "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5), "label_pos": (self.ui_panel_x + 20, 220)}, 
            {"label": "Number of Wumpus:", "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5), "label_pos": (self.ui_panel_x + 20, 300)}
        ]

        button_width = self.ui_panel_width - 40
        self.start_btn = Button("Start", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.stop_btn = Button("Stop", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_RED, Color.WHITE, "body", "center")
        self.back_btn = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 550, Color.DARK_RED, Color.WHITE, "body", "center")

        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)

        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.ui_panel_x + 20, 420, "left", "body")
        
        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_ui_panel_background(self, surface):
        panel_surface = pygame.Surface((self.ui_panel_width, SCREEN_HEIGHT))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(150)
        surface.blit(panel_surface, (self.ui_panel_x, 0))

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_ui_panel_background(surface)
        self.title.draw(surface)

        for item in self.slider_list:
            label = Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body")
            label.draw(surface)
            item["slider"].draw(surface)

        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        status_msg = "Ready to start"
        if self.is_playing:
            status_msg = f"Step {self.game_step}: {self.current_action}"
        elif self.game_finished:
            status_msg = "Game finished!"
        
        self.status_text.text = status_msg
        self.status_text.draw(surface)

        if self.is_playing:
            self.stop_btn.draw(surface)
        else:
            self.start_btn.draw(surface)
        self.back_btn.draw(surface)

        if self.Game:
            self.draw_game_map(surface)

    def game_loop_worker(self):
        try:
            while self.is_playing and self.Game:
                self.Game.agent_take_percepts()  
                self.Game.agent.get_KB_from_percepts()
                action = self.Game.agent.choose_action('random')   
                self.Game.actions.append(action)
                self.Game.update_score()
                
                step_event = pygame.event.Event(GAME_STEP_EVENT, {'action': action, 'step': len(self.Game.actions)})
                pygame.event.post(step_event)
                
                print(f'Iter {len(self.Game.actions)}: Action: {action}')
                
                game_ended = False
                if action == "climb out":
                    game_ended = True
                else:
                    flag = self.Game.map.update_map(action, self.Game.agent)
                    if not flag:
                        self.Game.actions.append("die")
                        self.Game.update_score()
                        game_ended = True
                    elif len(self.Game.actions) > 20:
                        print("Too many actions, stopping the game.")
                        game_ended = True
                
                if game_ended:
                    end_event = pygame.event.Event(GAME_END_EVENT, {'final_score': getattr(self.Game, 'score', 0)})
                    pygame.event.post(end_event)
                    break
                
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Game loop error: {e}")
            pygame.event.post(pygame.event.Event(GAME_END_EVENT, {'error': str(e)}))

    def start_game(self):
        size = int(self.slider_list[0]["slider"].value)
        pit = self.slider_list[1]["slider"].value
        wumpus = int(self.slider_list[2]["slider"].value)
        hard = self.toggle.value
        
        print("Game configuration: ", size, pit, wumpus, hard)
        
        self.Game = Game(size, pit, wumpus, hard)
        self.is_playing = True
        self.game_finished = False
        self.game_step = 0
        self.current_action = ""
        
        self.game_thread = threading.Thread(target=self.game_loop_worker, daemon=True)
        self.game_thread.start()

    def stop_game(self):
        self.is_playing = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=1.0)

    def update(self):
        for item in self.slider_list:
            item["slider"].update()
        self.toggle.update()

    def draw_game_map(self, surface):
        if not self.Game or not self.Game.map:
            return

        self.Game.map.draw(surface)
        self.Game.agent.draw(surface)
        
    def handle_event(self, event):
        if event.type == GAME_STEP_EVENT:
            self.current_action = event.action
            self.game_step = event.step
            return
        elif event.type == GAME_END_EVENT:
            self.is_playing = False
            self.game_finished = True
            if hasattr(event, 'error'):
                print(f"Game ended with error: {event.error}")
            return

        if not self.is_playing:
            for item in self.slider_list:
                item["slider"].handle_event(event)
            self.toggle.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            if self.back_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.stop_game()
                self.screen_manager.set_screen("menu")
            elif self.start_btn.is_point_inside(event.pos[0], event.pos[1]) and not self.is_playing:
                self.start_game()
            elif self.stop_btn.is_point_inside(event.pos[0], event.pos[1]) and self.is_playing:
                self.stop_game()

    def cleanup(self):
        self.stop_game()