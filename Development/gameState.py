from Development.agent import Agent
from Development.map import Map
class Game:
    def __init__(self, size=4, pit_density=0.2, num_wumpus=2, hard_mode=False):
        self.map = Map(size, pit_density, num_wumpus)
        self.agent = Agent(num_wumpus, size)
        self.point = 0
    def agent_take_percepts(self):
        new_percepts = self.map.get_percepts_for_agent(self.agent)
        if self.agent.percepts:
            self.agent.percepts.extend(new_percepts)
        else:
            self.agent.percepts = new_percepts

    def update_score(self):
        self.point = 0
        for action in self.agent.actions:
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

    def play(self):
        pass 

    def pause(self):
        pass

