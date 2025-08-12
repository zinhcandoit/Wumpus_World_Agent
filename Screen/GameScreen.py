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

# Custom events
GAME_STEP_EVENT = pygame.USEREVENT + 1
GAME_END_EVENT = pygame.USEREVENT + 2

class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)

        self.map_size = 8
        self.pit_density = 0.2
        self.num_wumpus = 2
        self.hard_mode = False

        self.Game = None
        self.is_playing = False
        self.game_thread = None
        
        # Game state
        self.current_action = ""
        self.game_step = 0
        self.game_finished = False

        self.ui_panel_width = SCREEN_WIDTH // 4
        self.ui_panel_x = SCREEN_WIDTH - self.ui_panel_width  
        self.ui_center_x = self.ui_panel_x + self.ui_panel_width // 2

        # Slider list kèm label
        self.slider_list = [
            {
                "label": "Map Size:",
                "slider": Slider(self.ui_center_x, 145, self.ui_panel_width // 3 + 20, 20, 8, 4, 12),
                "label_pos": (self.ui_panel_x + 20, 140)
            }, 
            {
                "label": "Pit Density:",
                "slider": Slider(self.ui_center_x, 225, self.ui_panel_width // 3 + 20, 20, 0.2, 0.1, 0.5),
                "label_pos": (self.ui_panel_x + 20, 220)
            }, 
            {
                "label": "Number of Wumpus:",
                "slider": Slider(self.ui_center_x, 305, self.ui_panel_width // 3 + 20, 20, 2, 1, 5),
                "label_pos": (self.ui_panel_x + 20, 300)
            }, 
        ]

        # Buttons
        button_width = self.ui_panel_width - 40
        self.start_btn = Button("Start", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_GREEN, Color.WHITE, "body", "center")
        self.stop_btn = Button("Stop", "Arial", button_width, 40, self.ui_center_x, 490, Color.DARK_RED, Color.WHITE, "body", "center")
        self.back_btn = Button("Back to menu", "Arial", button_width, 40, self.ui_center_x, 550, Color.DARK_RED, Color.WHITE, "body", "center")

        # Toggle
        self.toggle_label = Text("Hard Mode", "Arial", Color.WHITE, self.ui_panel_x + 20, 360, "left", "body")
        self.toggle = Toggle(self.ui_panel_x + self.ui_panel_width - 60, 355, value=False)

        # Title & Status
        self.title = Text("Game Information", "Arial", Color.WHITE, self.ui_center_x, 50, "center", "sub_title")
        self.status_text = Text("Ready to start", "Arial", Color.WHITE, self.ui_panel_x + 20, 420, "left", "body")
        
        # Background
        self.bg = Image("assets/background/intro.jpg", SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)

    def draw_bg(self, surface):
        self.bg.draw(surface)
        surface.blit(self.overlay, (0, 0))

    def draw_title(self, surface):
        self.title.draw(surface)

    def draw_ui_panel_background(self, surface):
        panel_surface = pygame.Surface((self.ui_panel_width, SCREEN_HEIGHT))
        panel_surface.fill((0, 0, 0))
        panel_surface.set_alpha(150)
        surface.blit(panel_surface, (self.ui_panel_x, 0))

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_ui_panel_background(surface)
        self.draw_title(surface)

        # Slider + label
        for item in self.slider_list:
            label = Text(item["label"], "Arial", Color.WHITE, item["label_pos"][0], item["label_pos"][1], "left", "body")
            label.draw(surface)
            item["slider"].draw(surface)

        # Toggle
        self.toggle_label.draw(surface)
        self.toggle.draw(surface)

        # Status text
        if self.is_playing:
            status_msg = f"Step {self.game_step}: {self.current_action}"
        elif self.game_finished:
            status_msg = "Game finished!"
        else:
            status_msg = "Ready to start"
        
        self.status_text.text = status_msg
        self.status_text.draw(surface)

        # Buttons
        if self.is_playing:
            self.stop_btn.draw(surface)
        else:
            self.start_btn.draw(surface)
        self.back_btn.draw(surface)

        # Game map
        if self.Game:
            self.draw_game_map(surface)

    def game_loop_worker(self):
        """Worker thread cho game logic"""
        try:
            while self.is_playing and self.Game:
                # Game step
                self.Game.agent_take_percepts()  
                self.Game.agent.get_KB_from_percepts()
                action = self.Game.agent.choose_action('random')   
                self.Game.actions.append(action)
                self.Game.update_score()
                
                # Post event về main thread
                step_event = pygame.event.Event(GAME_STEP_EVENT, {
                    'action': action,
                    'step': len(self.Game.actions)
                })
                pygame.event.post(step_event)
                
                print(f'Iter {len(self.Game.actions)}: Action: {action}')
                
                # Check game end
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
                    end_event = pygame.event.Event(GAME_END_EVENT, {
                        'final_score': getattr(self.Game, 'score', 0)
                    })
                    pygame.event.post(end_event)
                    break
                
                # Delay
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
        
        # Khởi động worker thread
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
        
        # Map drawing area (left side of screen, excluding UI panel)
        map_area_width = self.ui_panel_x - 40  # 40px padding
        map_area_height = SCREEN_HEIGHT - 80   # 80px padding (40 top, 40 bottom)
        map_start_x = 20
        map_start_y = 40
        
        # Calculate cell size based on map size and available space
        cell_size = min(map_area_width // self.Game.map.size, 
                    map_area_height // self.Game.map.size)
        
        # Center the map in the available area
        total_map_width = cell_size * self.Game.map.size
        total_map_height = cell_size * self.Game.map.size
        map_offset_x = map_start_x + (map_area_width - total_map_width) // 2
        map_offset_y = map_start_y + (map_area_height - total_map_height) // 2
        
        # Draw grid background
        for row in range(self.Game.map.size):
            for col in range(self.Game.map.size):
                x = map_offset_x + col * cell_size
                y = map_offset_y + row * cell_size
                
                # Cell background (alternating colors for better visibility)
                if (row + col) % 2 == 0:
                    cell_color = (40, 40, 40)  # Dark gray
                else:
                    cell_color = (60, 60, 60)  # Lighter gray
                
                pygame.draw.rect(surface, cell_color, (x, y, cell_size, cell_size))
                
                # Cell border
                pygame.draw.rect(surface, Color.WHITE, (x, y, cell_size, cell_size), 1)
        
        # Draw map contents
        for row in range(self.Game.map.size):
            for col in range(self.Game.map.size):
                x = map_offset_x + col * cell_size
                y = map_offset_y + row * cell_size
                cell_center_x = x + cell_size // 2
                cell_center_y = y + cell_size // 2
                
                cell_contents = self.Game.map.grid[row][col]
                
                # Draw multiple elements in the same cell
                element_positions = []
                
                # Wumpus (highest priority - center)
                if 'wumpus' in cell_contents:
                    pygame.draw.circle(surface, Color.DARK_RED, (cell_center_x, cell_center_y), cell_size // 4)
                    # Draw eyes
                    eye_offset = cell_size // 8
                    pygame.draw.circle(surface, Color.WHITE, 
                                    (cell_center_x - eye_offset, cell_center_y - eye_offset), 3)
                    pygame.draw.circle(surface, Color.WHITE, 
                                    (cell_center_x + eye_offset, cell_center_y - eye_offset), 3)
                    element_positions.append('center')
                
                # Pit (center if no wumpus)
                elif 'pit' in cell_contents:
                    pygame.draw.circle(surface, Color.BLACK, (cell_center_x, cell_center_y), cell_size // 3)
                    pygame.draw.circle(surface, Color.DARK_GRAY, (cell_center_x, cell_center_y), cell_size // 4)
                    element_positions.append('center')
                
                # Gold (top-right corner)
                if 'gold' in cell_contents:
                    gold_x = x + cell_size - cell_size // 4
                    gold_y = y + cell_size // 4
                    pygame.draw.circle(surface, Color.YELLOW, (gold_x, gold_y), cell_size // 6)
                    # Draw gold shine
                    pygame.draw.circle(surface, Color.WHITE, (gold_x - 2, gold_y - 2), 2)
                    element_positions.append('top-right')
                
                # Agent (center if no wumpus/pit, otherwise bottom)
                if 'agent' in cell_contents:
                    agent = self.Game.agent
                    if 'center' not in element_positions:
                        agent_x, agent_y = cell_center_x, cell_center_y
                    else:
                        agent_x, agent_y = cell_center_x, y + cell_size - cell_size // 4
                    
                    # Agent body
                    pygame.draw.circle(surface, Color.BLUE, (agent_x, agent_y), cell_size // 6)
                    
                    # Agent direction indicator
                    direction_offsets = {
                        'N': (0, -cell_size // 4),
                        'S': (0, cell_size // 4),
                        'E': (cell_size // 4, 0),
                        'W': (-cell_size // 4, 0)
                    }
                    
                    if hasattr(agent, 'direction') and agent.direction in direction_offsets:
                        dx, dy = direction_offsets[agent.direction]
                        arrow_end_x = agent_x + dx
                        arrow_end_y = agent_y + dy
                        pygame.draw.line(surface, Color.WHITE, (agent_x, agent_y), 
                                    (arrow_end_x, arrow_end_y), 2)
                        # Arrow head
                        pygame.draw.circle(surface, Color.WHITE, (arrow_end_x, arrow_end_y), 2)
                
                # Percept indicators (smaller icons in corners)
                percept_size = cell_size // 8
                
                # Check if this cell has stench (adjacent to wumpus)
                if self.Game.map.has_adjacent(row, col, 'wumpus'):
                    stench_x = x + cell_size // 8
                    stench_y = y + cell_size // 8
                    pygame.draw.circle(surface, Color.GREEN, (stench_x, stench_y), percept_size)
                    # Draw wavy lines for stench
                    for i in range(3):
                        start_y = stench_y - percept_size + i * 3
                        end_y = start_y
                        pygame.draw.line(surface, Color.DARK_GREEN, 
                                    (stench_x - percept_size, start_y), 
                                    (stench_x + percept_size, end_y), 1)
                
                # Check if this cell has breeze (adjacent to pit)
                if self.Game.map.has_adjacent(row, col, 'pit'):
                    breeze_x = x + cell_size - cell_size // 8
                    breeze_y = y + cell_size // 8
                    pygame.draw.circle(surface, Color.CYAN, (breeze_x, breeze_y), percept_size)
                    # Draw wind lines for breeze
                    for i in range(2):
                        start_x = breeze_x - percept_size + i * 4
                        pygame.draw.line(surface, Color.DARK_BLUE, 
                                    (start_x, breeze_y - percept_size), 
                                    (start_x + 2, breeze_y + percept_size), 1)
        
        # Draw coordinate labels
        font = pygame.font.Font(None, max(16, cell_size // 4))
        
        # Column labels (bottom)
        for col in range(self.Game.map.size):
            x = map_offset_x + col * cell_size + cell_size // 2
            y = map_offset_y + self.Game.map.size * cell_size + 10
            label = font.render(str(col), True, Color.WHITE)
            label_rect = label.get_rect(center=(x, y))
            surface.blit(label, label_rect)
        
        # Row labels (left side)
        for row in range(self.Game.map.size):
            x = map_offset_x - 20
            y = map_offset_y + row * cell_size + cell_size // 2
            label = font.render(str(row), True, Color.WHITE)
            label_rect = label.get_rect(center=(x, y))
            surface.blit(label, label_rect)
        
        # Draw legend
        legend_y = map_offset_y + total_map_height + 40
        legend_font = pygame.font.Font(None, 20)
        
        legend_items = [
            ("Agent", Color.BLUE),
            ("Wumpus", Color.DARK_RED),
            ("Pit", Color.BLACK),
            ("Gold", Color.YELLOW),
            ("Stench", Color.GREEN),
            ("Breeze", Color.CYAN)
        ]
        
        for i, (name, color) in enumerate(legend_items):
            legend_x = map_offset_x + (i % 3) * 120
            legend_row_y = legend_y + (i // 3) * 25
            
            pygame.draw.circle(surface, color, (legend_x, legend_row_y), 8)
            label = legend_font.render(name, True, Color.WHITE)
            surface.blit(label, (legend_x + 15, legend_row_y - 8))
        
        # Game info overlay
        info_y = map_offset_y - 30
        info_font = pygame.font.Font(None, 24)
        
        if hasattr(self.Game, 'agent'):
            agent_info = f"Agent: ({self.Game.agent.location[0]}, {self.Game.agent.location[1]}) facing {getattr(self.Game.agent, 'direction', 'N')}"
            if hasattr(self.Game.agent, 'has_gold') and self.Game.agent.has_gold:
                agent_info += " [Has Gold]"
            if hasattr(self.Game.agent, 'has_arrow') and not self.Game.agent.has_arrow:
                agent_info += " [No Arrow]"
            
            info_surface = info_font.render(agent_info, True, Color.WHITE)
            surface.blit(info_surface, (map_offset_x, info_y))
        
        # Score display (if available)
        if hasattr(self.Game, 'score'):
            score_text = f"Score: {self.Game.score}"
            score_surface = info_font.render(score_text, True, Color.WHITE)
            surface.blit(score_surface, (map_offset_x, info_y + 25))
        

    def handle_event(self, event):
        # Handle custom game events
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

        # Regular event handling
        if not self.is_playing:
            for item in self.slider_list:
                item["slider"].handle_event(event)
            self.toggle.handle_event(event)
            self.hard_mode = self.toggle.value

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