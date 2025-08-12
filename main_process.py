from Development.gameState import Game
from Development.definition import Literal
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
        action = game.agent.choose_action('random')   # We will use random agent / Logic agent for choosing action
        game.actions.append(action)
        game.update_score()
        if action == "climb out":
            break
        flag = game.map.update_map(action, game.agent)
        print('Iter', len(game.actions), 'Action:', action)
        print_map(game.map)
        if flag == False:
            game.actions.append("die")
            game.update_score()
            break
        if (len(game.actions) > 20):
            print("Too many actions, stopping the game.")
            break
    return game.point, game.actions

point, action = play(4, 0.2, 2)  # Example call to play the game with a 4x4 map, 20% pit density, and 2 wumpuses
print(f"Final score: {point}")
print(f"Actions taken: {action}")