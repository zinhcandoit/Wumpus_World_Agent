from agent import Agent
from map import Map
class Game:
    def __init__(self, size, pit_density=0.2, num_wumpus=2):
        self.map = Map(size, pit_density, num_wumpus)
        self.agent = Agent(num_wumpus, size)
        self.point = 0
        self.actions = []

    def get_percepts(self):
        return self.map.get_percepts_for_agent(self.agent)

    def update_score(self):
        self.point = 0
        for action in self.actions:
            if action == "climb out":
                self.point += (1000 if self.agent.has_gold else 0)
            elif action == "turn left" or action == "turn right" or action == "move":
                self.point -= 1
            elif action == "shoot":
                self.point -= 10
            elif action == "grab":
                self.point += 10
            elif action == "die":
                self.point -= 1000

