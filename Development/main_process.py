from gameState import Game

def play(size, pit_density, num_wumpus):
    game = Game(size, pit_density, num_wumpus)
    while True:
        game.agent.percepts.append(game.map.get_percepts_for_agent(game.agent))
        action = game.agent.choose_action()   # We will use random agent / Logic agent for choosing action
        game.actions.append(action)
        game.update_score()
        if action == "climb out":
            break
        flag = game.map.update_map(action, game.agent)
        if flag == False:
            game.actions.append("die")
            game.update_score()
            break