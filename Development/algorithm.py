from Development.definition import Literal
# Cause w can move!
dynamic_literal = {"wumpus", "stench"}

def make_clause(literals):
            """Canonicalize clause -> frozenset; drop tautologies (A and ¬A)."""
            s = set(literals)
            # drop tautology: if a (name,pos) appears with both negate True/False -> ignore
            for name_pos in {(lit.name, lit.pos) for lit in s}:
                negs = {lit.negate for lit in s if (lit.name, lit.pos) == name_pos}
                if len(negs) > 1:
                    return None
            return frozenset(s)

def _var_key(lit):
    # Add step count to dynamic variable
    if lit.name in dynamic_literal:
        return (lit.name, lit.pos, lit.at_step)
    return (lit.name, lit.pos)

def prune_by_radius(agent, R=3, keep_static=True):
    ay, ax = agent.location

    def near(pos):
        return abs(pos[0] - ay) + abs(pos[1] - ax) <= R

    new_KB = set()
    for clause in agent.KB:
        # clause toàn literal tĩnh?
        all_static = all(lit.name not in dynamic_literal for lit in clause)
        if keep_static and all_static:
            new_KB.add(clause)
            continue

        # giữ nếu có literal nào ở gần
        if any(near(lit.pos) for lit in clause):
            new_KB.add(clause)

    agent.KB = new_KB

def _symbols_from_KB(KB):
    """Return ordered list of propositional symbols as tuples (name,pos)."""
    vars_set = set()
    for clause in KB:
        for lit in clause:
            vars_set.add(_var_key(lit))
    # deterministic order
    return sorted(vars_set, key=lambda t: (t[0], t[1], t[2] if len(t) > 2 else -1))

def _pl_true_literal(literal, model):
    """Evaluate a literal under (complete) model dict var->bool."""
    var = _var_key(literal)
    val = model.get(var, False)  # if not present, default False
    return (not literal.negate and val) or (literal.negate and not val)


def _clause_status_under_partial(clause, model):
    """
    Evaluate clause under partial assignment (model may be partial).
    Return:
      True  -> clause already satisfied (some literal true)
      False -> clause already contradicted (all literals assigned and none true)
      None  -> undecided (no literal true yet, some unassigned remain)
    """
    any_unassigned = False
    for lit in clause:
        var = _var_key(lit)
        if var in model:
            val = model[var]
            lit_true = (not lit.negate and val) or (lit.negate and not val)
            if lit_true:
                return True
        else:
            any_unassigned = True
    return None if any_unassigned else False

def _tt_check_all(KB, alpha_literal, symbols, model):
    """
    TT-CHECK-ALL recursively.
    symbols: list of vars (name,pos)
    model: dict partial assignment { (name,pos): bool }
    Return True/False according to TT-ENTAILS pseudocode:
      - True means *so far* no counterexample found in this branch (i.e., branch supports entailment)
    Implementation note:
      - We prune branches where KB is already impossible (clause false): per pseudocode, treat as True (vacuous)
    """
    # if no symbols left, evaluate KB and alpha under (complete) model
    if not symbols:
        # model is complete
        # if KB true under this model -> return truth of alpha under model
        # else (KB false) -> return True (vacuously)
        kb_holds = True
        for clause in KB:
            # clause must have at least one literal true
            satisfied = False
            for lit in clause:
                if _pl_true_literal(lit, model):
                    satisfied = True
                    break
            if not satisfied:
                kb_holds = False
                break
        if kb_holds:
            return _pl_true_literal(alpha_literal, model)
        else:
            return True  # when KB false, branch vacuously supports entailment

    # pruning: if some clause is already false under partial model, then KB false for any completion => return True
    # (this matches the TT pseudocode behavior: branch does not produce counterexample)
    for clause in KB:
        st = _clause_status_under_partial(clause, model)
        if st is False:
            return True

    # choose next symbol (take first)
    P = symbols[0]
    rest = symbols[1:]

    # set P = true
    model[P] = True
    res1 = _tt_check_all(KB, alpha_literal, rest, model)
    # set P = false
    model[P] = False
    res2 = _tt_check_all(KB, alpha_literal, rest, model)
    # clean up
    del model[P]
    return res1 and res2


def tt_entails(KB, alpha_literal):
    """
    Return True if KB entails alpha_literal (alpha_literal is a Literal instance).
    Implements TT-ENTAILS by calling TT-CHECK-ALL.
    """
    symbols = _symbols_from_KB(KB)
    # ensure alpha's variable in symbols list (if not, add it)
    alpha_var = _var_key(alpha_literal)
    if alpha_var not in symbols:
        symbols = symbols + [alpha_var]
    return _tt_check_all(KB, alpha_literal, symbols, {})

'''def classify_all_literals_now(KB, current_step):
    result = {}
    if not KB:
        return result
    sample_lit = next(iter(next(iter(KB))))
    LitType = type(sample_lit)

    vars_set = set((lit.name, lit.pos) for clause in KB for lit in clause)

    for name, pos in sorted(vars_set, key=lambda t: (t[0], t[1])):
        pos = tuple(pos)
        if name in dynamic_literal:
            pos_lit = LitType(name, pos, False, current_step)
            neg_lit = LitType(name, pos, True,  current_step)
        else:
            pos_lit = LitType(name, pos, False)
            neg_lit = LitType(name, pos, True)

        if tt_entails(KB, pos_lit):
            result[(name, pos)] = "UNSAFE"
        elif tt_entails(KB, neg_lit):
            result[(name, pos)] = "SAFE"
        else:
            result[(name, pos)] = "UNKNOWN"
    return result'''

def build_focus_pairs_for_decision(agent):
    y, x = agent.location
    nbr = [(y, x+1), (y+1, x), (y, x-1), (y-1, x)]
    focus = set()
    if agent.has_gold == False:
        focus.add(("gold", (y,x)))
    for nb in nbr:
        if 0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known:
            focus.add(("wumpus", nb))
            focus.add(("pit", nb))

    # Mở rộng cho SHOOT (bắn xa)
    if agent.has_arrow:
        # 1) nếu đã có dự đoán trước
        if getattr(agent, 'wumpus_die', None) is not None:
            focus.add(("wumpus", tuple(agent.wumpus_die)))
        else:
        # 2) thêm ray theo hướng hiện tại
            direction_moves = {'N': (-1, 0), "S": (1, 0), "W": (0, -1), 'E': (0, 1)}
            dy, dx = direction_moves[agent.direction]
            y, x = agent.location
            for i in range(1, agent.size_known):
                cell = (y + i*dy, x + i*dx)
                if not (0 <= cell[0] < agent.size_known and 0 <= cell[1] < agent.size_known):
                    break
                focus.add(("wumpus", cell))
    return focus

def classify_all_local(KB, current_step, focus_pairs):
    """
    Chỉ entail trên các (name,pos) trong focus_pairs.
    Trả về {(name,pos): 'SAFE'|'UNSAFE'|'UNKNOWN'}.
    """
    if not KB:
        return {k: "UNKNOWN" for k in focus_pairs}

    sample_lit = next(iter(next(iter(KB))))
    Lit = type(sample_lit)

    out = {}
    for (name, pos) in focus_pairs:
        pos = tuple(pos)
        if name in dynamic_literal:
            pos_lit = Lit(name, pos, False, current_step)
            neg_lit = Lit(name, pos, True,  current_step)
        else:
            pos_lit = Lit(name, pos, False)
            neg_lit = Lit(name, pos, True)

        if tt_entails(KB, pos_lit):
            out[(name, pos)] = "UNSAFE"
        elif tt_entails(KB, neg_lit):
            out[(name, pos)] = "SAFE"
        else:
            out[(name, pos)] = "UNKNOWN"
    return out

def get_possible_actions_now(agent, status_map):
    actions = []
    direction_moves = {'N': (-1, 0), "S": (1, 0), "W": (0, -1), 'E': (0, 1)}

    if status_map.get(("gold", agent.location)) == "UNSAFE" and not agent.has_gold:
        actions.append("grab")

    if agent.location == agent.start_location:
        actions.append("climb out")
    
    actions.extend(["turn left", "turn right"])

    dy, dx = direction_moves[agent.direction]
    front_cell = (agent.location[0] + dy, agent.location[1] + dx)
    if 0 <= front_cell[0] < agent.size_known and 0 <= front_cell[1] < agent.size_known:
        pit_state = status_map.get(("pit", front_cell), "UNKNOWN")
        w_state = status_map.get(("wumpus", front_cell), "UNKNOWN")
            # không mùi -> cho move nếu không bị đánh dấu UNSAFE
        if pit_state != "UNSAFE" and w_state != "UNSAFE":
            actions.append("move")
    
    w_infront = False
    for i in range(1, agent.size_known):
        nb = (agent.location[0] + i * dy, agent.location[1] + i * dx)
        if not (0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known):
            break  # out of bounds
        if status_map.get(("wumpus", nb), "UNKNOWN") == "UNSAFE":
            w_infront = True
            agent.wumpus_die = nb
        else: w_infront = False
    if agent.has_arrow and w_infront:
        actions.append("shoot")

    return actions
