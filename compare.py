from Development.gameState import Game
from Development.algorithm import prune_by_radius

class Compare:
    STRATEGY = {"random", "heuristic"}

    def __init__(self, size=7, pit_density=0.1, num_wumpus=1, times=10, max_actions=300):
        self.size = size
        self.pit_density = pit_density
        self.num_wumpus = num_wumpus
        self.times = times
        self.max_actions = max_actions

    @staticmethod
    def _valid_pair(a, b):
        if a == b:
            return False
        if a not in Compare.STRATEGY:
            return False
        if b not in Compare.STRATEGY:
            return False
        return True

    def _play(self, strategy):
        game = Game(self.size, self.pit_density, self.num_wumpus)
        is_success = False

        while True:
            game.agent_take_percepts()
            game.agent.get_KB_from_percepts()
            prune_by_radius(game.agent, game.agent.size_known // 2 if game.agent.size_known // 2 > 3 else 3, True)
            action = game.agent.choose_action(strategy)
            game.agent.actions.append(action)
            game.update_score()

            if action == "climb out":
                is_success = bool(game.agent.has_gold)
                break

            flag = game.map.update_map(action, game.agent)
            if flag is False:
                game.agent.actions.append("die")
                game.update_score()
                break

            if len(game.agent.actions) > self.max_actions:
                break

        return game.point, game.agent.actions, is_success

    def compare_success_rate(self, strategyA, strategyB):
        if not self._valid_pair(strategyA, strategyB):
            raise ValueError("Chiến lược không hợp lệ hoặc trùng nhau")

        succA = 0
        for _ in range(self.times):
            _, _, ok = self._play(strategyA)
            if ok:
                succA += 1
        rateA = succA / self.times

        succB = 0
        for _ in range(self.times):
            _, _, ok = self._play(strategyB)
            if ok:
                succB += 1
        rateB = succB / self.times

        return rateA, rateB

    def compare_solution_length(self, strategyA, strategyB):
        if not self._valid_pair(strategyA, strategyB):
            raise ValueError("Chiến lược không hợp lệ hoặc trùng nhau")

        totalA = 0
        for _ in range(self.times):
            _, actions, _ = self._play(strategyA)
            totalA += len(actions)
        lenA = totalA / self.times

        totalB = 0
        for _ in range(self.times):
            _, actions, _ = self._play(strategyB)
            totalB += len(actions)
        lenB = totalB / self.times

        return lenA, lenB

    def run(self, strategyA, strategyB):
        rateA, rateB = self.compare_success_rate(strategyA, strategyB)
        lenA, lenB = self.compare_solution_length(strategyA, strategyB)
        return {
            "strategyA": strategyA,
            "strategyB": strategyB,
            "success_rate": {strategyA: rateA, strategyB: rateB},
            "avg_length": {strategyA: lenA, strategyB: lenB},
        }

    def print_table(self, result):
        a = result["strategyA"]
        b = result["strategyB"]
        rateA = result["success_rate"][a]
        rateB = result["success_rate"][b]
        lenA = result["avg_length"][a]
        lenB = result["avg_length"][b]

        headers = ["Chỉ số", a, b]
        rows = [
            ["Tỉ lệ thành công", f"{rateA:.2%}", f"{rateB:.2%}"],
            ["Độ dài trung bình", f"{lenA:.2f}", f"{lenB:.2f}"],
        ]

        colw = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
        def fmt_row(r): return " | ".join(str(v).ljust(w) for v, w in zip(r, colw))
        line = "-+-".join("-" * w for w in colw)

        print(fmt_row(headers))
        print(line)
        for r in rows:
            print(fmt_row(r))


if __name__ == "__main__":
    cmp = Compare(size=4, pit_density=0.1, num_wumpus=1, times=10)
    result = cmp.run("random", "heuristic")
    cmp.print_table(result)
