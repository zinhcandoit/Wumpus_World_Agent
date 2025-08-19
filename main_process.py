from Development.gameState import Game
from Development.algorithm import prune_by_radius
#from Development.algorithm import prune_by_radius
def print_map(map):
    for row in map.grid:
        print(" | ".join(" ".join(cell) for cell in row))
    print()
def play(size, pit_density, num_wumpus):
    game = Game(size, pit_density, num_wumpus)
    print("Agent starting at:", game.agent.location)
    print("Initial Map:")
    print_map(game.map)
    print('Map size:', game.agent.size_known)
    while True:
        game.agent_take_percepts()  # Agent takes percepts from the map
        game.agent.get_KB_from_percepts()
        prune_by_radius(game.agent, game.agent.size_known // 2 if game.agent.size_known // 2 > 3 else 3, True) # Pruning KB
        action = game.agent.choose_action('random')   # We will use random agent / Logic agent for choosing action
        game.agent.actions.append(action)
        game.update_score()
        if action == "climb out":
            break
        flag = game.map.update_map(action, game.agent)
        print('Iter', len(game.agent.actions), 'Action:', action)
        print_map(game.map)
        if flag == False:
            game.agent.actions.append("die")
            game.update_score()
            break
        if (len(game.agent.actions) > 300):
            print("Too many actions, stopping the game.")
            break
    return game.point, game.agent.actions

point, action = play(6, 0.2, 2)  # Example call to play the game with a 4x4 map, 20% pit density, and 2 wumpuses
print(f"Final score: {point}")
print(f"Actions taken: {action}")