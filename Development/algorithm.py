from typing import List, Dict, Any
from dataclasses import dataclass
from definition import Literal
from agent import Agent

@dataclass(frozen=True)
# Hàm kiểm tra CNF có đúng không trong 1 model đầy đủ
def pl_true_cnf(cnf: List[List[Literal]], model: Dict[str, bool]) -> bool:
    """
    CNF = list các mệnh đề (clause), mỗi mệnh đề là list các Literal.
    Trả về True nếu CNF đúng trong model đã cho.
    """
    for clause in cnf:
        clause_val = False
        for lit in clause:
            if model.get(lit.name) is None:
                raise ValueError(f"Model chưa gán giá trị cho {lit.name}")
            lit_val = (model[lit.name] != lit.negated)
            clause_val = clause_val or lit_val
            if clause_val:  # Nếu mệnh đề đúng, bỏ qua phần còn lại
                break
        if not clause_val:  # Nếu có mệnh đề sai thì CNF sai
            return False
    return True

# Nếu alpha là Literal, chuyển thành CNF dạng [[Literal]]
def alpha_to_cnf(alpha: Any) -> List[List[Literal]]:
    if isinstance(alpha, Literal):
        return [[alpha]]
    return alpha  # giả sử alpha đã ở dạng CNF

# Lấy tất cả các biến xuất hiện trong KB và alpha
def extract_symbols(kb: List[List[Literal]], alpha: Any) -> List[str]:
    symbols = set()
    for clause in kb:
        for lit in clause:
            symbols.add(lit.name)
    alpha_cnf = alpha_to_cnf(alpha)
    for clause in alpha_cnf:
        for lit in clause:
            symbols.add(lit.name)
    return sorted(symbols)

# Hàm TT-CHECK-ALL
def tt_check_all(kb: List[List[Literal]], alpha: Any, symbols: List[str], model: Dict[str, bool]) -> bool:
    if not symbols:  # model đầy đủ
        if pl_true_cnf(kb, model):
            return pl_true_cnf(alpha_to_cnf(alpha), model)
        else:
            return True  # KB sai thì KB ⇒ α luôn đúng
    else:
        P = symbols[0]
        rest = symbols[1:]
        model_true = dict(model)
        model_true[P] = True
        model_false = dict(model)
        model_false[P] = False
        return (tt_check_all(kb, alpha, rest, model_true) and
                tt_check_all(kb, alpha, rest, model_false))

# Hàm TT-ENTAILS
def tt_entails(kb: List[List[Literal]], alpha: Any) -> bool:
    symbols = extract_symbols(kb, alpha)
    return tt_check_all(kb, alpha, symbols, {})

def get_possible_actions(agent: Agent):
    """
    Lấy tất cả các hành động có thể thực hiện của agent.
    """
    actions = []
    direction_moves = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
    dy, dx = direction_moves[agent.direction]
    if agent.has_arrow:
        for i in range(1, agent.size_known):
            new_y, new_x = agent.location[0] + i * dy, agent.location[1] + i * dx
            if 0 <= new_y < agent.size_known and 0 <= new_x < agent.size_known:
                wumpus_flag = [Literal("wumpus", (new_y, new_x), False)]
                if wumpus_flag in agent.KB:
                    actions.append("shoot")
                    break
            else: 
                break  # Ra khỏi map
    if not agent.has_gold:
        actions.append("grab")
    actions.append('turn left')
    actions.append('turn right')
    wumpus_flag = [Literal("wumpus", agent.location + tuple(dy, dx), False)]
    pit_flag = [Literal("pit", agent.location + tuple(dy, dx), False)]
    if wumpus_flag not in agent.KB and pit_flag not in agent.KB:
        actions.append("move")

