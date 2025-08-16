import pygame
import time
from Screen.BaseScreen import Screen
from Design.UI.text import Text
from Design.UI.slider import Slider
from Design.UI.button import Button
from Design.UI.toggle import Toggle
from Design.ImageManager.Image import Image
from Development.gameState import Game
from constant import *

class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.Game = None
        self.game_state = "IDLE"  # IDLE, SOLVING, PLAYING, FINISHED
        self.game_step = 0
        self.actions = []
        self.wumpus_actions = []
        self.point = 0
        self.current_action = ""
        self.last_step_ms = 0
        self.step_delay_ms = 350
        self.solving_start_time = 0
        
        # UI Setup
        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2
        
        self.slider_list = [
            {"label": "Map Size:", 
             "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12), 
             "label_pos": (self.ui_panel_x + 20, 140)},
            {"label": "Pit Density:", 
             "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5), 
             "label_pos": (self.ui_panel_x + 20, 220)},
            {"label": "Number of Wumpus:", 
             "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5), 
             "label_pos": (self.ui_panel_x + 20, 300)}
        ]
        
        button_width = self.ui_panel_width - 40
        self.play_btn = Button("Play", "Arial", button_width, 40, self.ui_center_x, 490, 
                              Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.stop_btn = Button("Stop", "Arial", button_width, 40, self.ui_center_x, 490, 
                              Color.DARK_RED, Color.WHITE, "body", "center")
        self.back_btn = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 550, 
                              Color.DARK_RED, Color.WHITE, "body", "center")
        
        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)
        
        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.ui_panel_x + 20, 420, "left", "body")
        self.debug_text = Text("", "Arial", Color.YELLOW, self.ui_panel_x + 20, 450, "left", "small")
        
        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

    # ---------- render helpers ----------
    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_ui_panel_background(self, surface):
        panel_surface = pygame.Surface((self.ui_panel_width, SCREEN_HEIGHT))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(150)
        surface.blit(panel_surface, (self.ui_panel_x, 0))

    def update_status_display(self):
        """Cập nhật text hiển thị trạng thái game"""
        if self.game_state == "IDLE":
            self.status_text.set_text("Ready to start")
            self.debug_text.set_text("")
        elif self.game_state == "SOLVING":
            elapsed = (pygame.time.get_ticks() - self.solving_start_time) / 1000
            self.status_text.set_text(f"Solving game... ({elapsed:.1f}s)")
            self.debug_text.set_text("AI is finding solution")
        elif self.game_state == "PLAYING":
            progress = f"{self.game_step + 1}/{len(self.actions)}"
            self.status_text.set_text(f"Playing: Step {progress}")
            self.debug_text.set_text(f"Action: {self.current_action}")
        elif self.game_state == "FINISHED":
            self.status_text.set_text(f"Finished! Score: {self.point}")
            self.debug_text.set_text(f"Total moves: {len(self.actions)}")

    # ---------- main draw ----------
    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_ui_panel_background(surface)
        
        # Draw UI elements
        self.title.draw(surface)
        
        for item in self.slider_list:
            label = Text(item["label"], "Arial", Color.WHITE, 
                        item["label_pos"][0], item["label_pos"][1], "left", "body")
            label.draw(surface)
            item["slider"].draw(surface)
        
        self.toggle_label.draw(surface)
        self.toggle.draw(surface)
        
        # Draw appropriate button based on game state
        if self.game_state in ["SOLVING", "PLAYING"]:
            self.stop_btn.draw(surface)
        else:
            self.play_btn.draw(surface)
        
        self.back_btn.draw(surface)
        
        # Update and draw status
        self.update_status_display()
        self.status_text.draw(surface)
        self.debug_text.draw(surface)
        
        # Draw game map if available
        self.draw_game_map(surface)

    # ---------- game control ----------
    def start_game(self):
        size = int(self.slider_list[0]["slider"].value)
        pit = self.slider_list[1]["slider"].value
        wumpus = int(self.slider_list[2]["slider"].value)
        hard = self.toggle.value    
        try:
            self.Game = Game(size, pit, wumpus, hard)
            self.game_state = "SOLVING"
            self.game_step = 0
            self.current_action = ""
            self.actions = []
            self.wumpus_actions = []
            self.point = 0
            self.solving_start_time = pygame.time.get_ticks()            
            
        except Exception as e:
            print(f"Error starting game: {e}")
            self.game_state = "IDLE"

    def solve_game(self):
        if self.Game and self.game_state == "SOLVING":
            try:
                print("Calling Game.play()...")
                self.point, self.actions, self.wumpus_actions = self.Game.play()
                
                print(f"Game solved successfully!")
                print(f"Final score: {self.point}")
                print(f"Total actions: {len(self.actions)}")
                print(f"Actions sequence: {self.actions}")
                print(f"Wumpus actions: {self.wumpus_actions}")
                
                # Chuyển sang trạng thái PLAYING để bắt đầu replay
                if self.actions:
                    self.game_state = "PLAYING"
                    self.last_step_ms = pygame.time.get_ticks()
                    print("Starting visual replay...")
                else:
                    self.game_state = "FINISHED"
                    print("No actions to replay")
                    
            except Exception as e:
                print(f"Error solving game: {e}")
                self.game_state = "FINISHED"
                self.point = 0
                self.actions = []
                self.wumpus_actions = []

    def stop_game(self):
        print("Game stopped by user")
        self.game_state = "FINISHED"
        self.current_action = ""

    def apply_visual_action(self, action):
        print(f"[Step {self.game_step + 1}] Applying action: {action}")
        self.Game.agent.apply_action(action)

    # ---------- update loop ----------
    def update(self):
        if self.game_state in ["IDLE", "FINISHED"]:
            for item in self.slider_list:
                item["slider"].update()
            self.toggle.update()
            
        if self.game_state == "IDLE":
            return
        
        if self.game_state == "SOLVING":
            self.solve_game()
            return
            
        if self.game_state == "PLAYING":
            now = pygame.time.get_ticks()
            
            if self.actions and (now - self.last_step_ms >= self.step_delay_ms):
                self.last_step_ms = now
                
                if self.game_step < len(self.actions):
                    action = self.actions[self.game_step]
                    self.current_action = str(action)
                    
                    try:
                        self.apply_visual_action(action)
                    except Exception as e:
                        print(f"Error in apply_visual_action: {e}")
                    
                    self.game_step += 1
                    
                    # Kiểm tra xem đã hết actions chưa
                    if self.game_step >= len(self.actions):
                        self.game_state = "FINISHED"
                        self.current_action = "Completed!"

    # ---------- map draw ----------
    def draw_game_map(self, surface):
        if not self.Game or not hasattr(self.Game, 'map') or not self.Game.map:
            return
            
        try:
            self.Game.map.draw(surface)
            if hasattr(self.Game, 'agent') and self.Game.agent:
                self.Game.agent.draw(surface)
        except Exception as e:
            print(f"Error drawing game map: {e}")

    # ---------- input ----------
    def handle_event(self, event):
        if self.game_state in ["IDLE", "FINISHED"]:
            for item in self.slider_list:
                item["slider"].handle_event(event)
            self.toggle.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Back to menu button
            if self.back_btn.is_point_inside(event.pos[0], event.pos[1]):
                self.stop_game()
                self.game_state = "IDLE"
                self.screen_manager.set_screen("menu")
            
            # Play button (chỉ khi IDLE hoặc FINISHED)
            elif (self.play_btn.is_point_inside(event.pos[0], event.pos[1]) and 
                  self.game_state in ["IDLE", "FINISHED"]):
                self.start_game()
            
            # Stop button (khi đang SOLVING hoặc PLAYING)
            elif (self.stop_btn.is_point_inside(event.pos[0], event.pos[1]) and 
                  self.game_state in ["SOLVING", "PLAYING"]):
                self.stop_game()