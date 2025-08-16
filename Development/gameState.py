from Development.agent import Agent
from Development.map import Map
from Development.algorithm import prune_by_radius
class Game:
    def __init__(self, size=4, pit_density=0.2, num_wumpus=2, hard_mode=False):
        self.map = Map(size, pit_density, num_wumpus)
        self.agent = Agent(num_wumpus, size)
        self.point = 0
        self.agent.actions = []
        self.wumpus_actions = []

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
        while True:
            self.agent_take_percepts()  # Agent takes percepts from the map
            self.agent.get_KB_from_percepts()
            prune_by_radius(self.agent, 3) # Pruning KB
            action = self.agent.choose_action('random')   # We will use random agent / Logic agent for choosing action
            self.agent.actions.append(action)
            self.update_score()
            if action == "climb out":
                break
            flag = self.map.update_map(action, self.agent)
            print('Iter', len(self.agent.actions), 'Action:', action)
            # print_map(self.map)
            if flag == False:
                self.agent.actions.append("die")
                self.update_score()
                break
            if (len(self.agent.actions) > 30):
                print("Too many actions, stopping the self.")
                break
        return self.point, self.agent.actions

    def pause(self):
        pass

