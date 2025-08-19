from Development.definition import Literal
# Cause w can move!
dynamic_literal = {"wumpus", "stench"}

# Type of percept is list -> change to frozenset to add to KB
def make_clause(literals):
    s = set(literals)
    if not s:
        return None
    # drop A v ¬A
    for name_pos in {(lit.name, lit.pos) for lit in s}:
        negs = {lit.negate for lit in s if (lit.name, lit.pos) == name_pos}
        if len(negs) > 1:
            return None
    return frozenset(s)

def _var_key(lit):
    # Add step count to wumpus
    if lit.name in dynamic_literal:
        return (lit.name, lit.pos, lit.at_step)
    return (lit.name, lit.pos)

def _symbols_from_KB(KB):
    vars_set = set()
    for clause in KB:
        for lit in clause:
            vars_set.add(_var_key(lit))
    # Deterministic order
    return sorted(vars_set, key=lambda t: (t[0], t[1], t[2] if len(t) > 2 else -1))

# Get boolean of a Literal
def _pl_true_literal(literal, model):
    var = _var_key(literal)
    val = model.get(var, False)  # If not present, default False
    return val if literal.negate == False else not val


def _clause_status_under_partial(clause, model):
    """
    Evaluate clause under partial assignment.
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
            lit_true = val if not lit.negate else not val
            if lit_true:
                return True
        else:
            any_unassigned = True
    return None if any_unassigned else False

def _tt_check_all(KB, alpha_literal, symbols, model):
    """
    Truth Table Entailment main process (recursive)
    symbols: list of vars (name,pos)
    model: dict partial assignment { (name,pos): bool }
    Return True/False:
      True means no counterexample found in this branch (i.e., branch supports entailment)
    """
    # if no symbols left, evaluate KB and alpha under model
    if not symbols:
        # model is complete
        # if KB true under this model -> return truth of alpha under model
        # else (KB false) -> return True
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
    for clause in KB:
        st = _clause_status_under_partial(clause, model)
        if st is False:
            return True

    # choose first next symbol
    P = symbols[0]
    rest = symbols[1:]

    # set P = true
    model[P] = True
    res1 = _tt_check_all(KB, alpha_literal, rest, model)
    # set P = false
    model[P] = False
    res2 = _tt_check_all(KB, alpha_literal, rest, model)

    del model[P]
    return res1 and res2


def tt_entails(KB, alpha_literal):
    """
    Return True if KB entails alpha_literal (alpha_literal is a Literal instance).
    Implements TT-ENTAILS by calling TT-CHECK-ALL.
    """
    symbols = _symbols_from_KB(KB)
    # Ensure alpha's variable in symbols list
    alpha_var = _var_key(alpha_literal)
    if alpha_var not in symbols:
        symbols = symbols + [alpha_var]
    return _tt_check_all(KB, alpha_literal, symbols, {})

def classify_all_local(KB, current_step, focus_pairs):
    if not KB:
        return {k: "UNKNOWN" for k in focus_pairs}

    out = {}
    for (name, pos) in focus_pairs:
        pos = tuple(pos)
        if name in dynamic_literal:
            pos_lit = Literal(name, pos, False, current_step)
            neg_lit = Literal(name, pos, True,  current_step)
        else:
            pos_lit = Literal(name, pos, False)
            neg_lit = Literal(name, pos, True)

        if tt_entails(KB, pos_lit):
            out[(name, pos)] = "UNSAFE"
        elif tt_entails(KB, neg_lit):
            out[(name, pos)] = "SAFE"
        else:
            out[(name, pos)] = "UNKNOWN"
    return out

# For agent
def prune_by_radius(agent, R=3, keep_static=True):
    ay, ax = agent.location

    def near(pos):
        return abs(pos[0] - ay) + abs(pos[1] - ax) <= R

    new_KB = set()
    for clause in agent.KB:
        # Keep static clause
        all_static = all(lit.name != dynamic_literal for lit in clause)
        if keep_static and all_static:
            new_KB.add(clause)
            continue

        # Keep local dynamic clause
        if any(near(lit.pos) for lit in clause):
            new_KB.add(clause)

    agent.KB = new_KB

def build_focus_pairs_for_decision(agent):
    y, x = agent.location
    nbr = [(y, x+1), (y+1, x), (y, x-1), (y-1, x), (y, x)]
    focus = set()
    if not agent.has_gold:
        focus.add(("gold", (y, x)))

    # Agent self-awareness of wumpus every 5 moves
    focus.add(("stench", (y, x)))
    for nb in nbr[:-1]:
        if 0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known:
            focus.add(("stench", nb))

    for nb in nbr:
        if 0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known:
            focus.add(("wumpus", nb))
            focus.add(("pit", nb))

    # Shoot
    if agent.has_arrow:
        if getattr(agent, 'wumpus_die', None) is not None:
            focus.add(("wumpus", tuple(agent.wumpus_die)))
        else:
            direction_moves = {'N': (-1, 0), "S": (1, 0), "W": (0, -1), 'E': (0, 1)}
            dy, dx = direction_moves[agent.direction]
            for i in range(1, agent.size_known):
                cell = (y + i*dy, x + i*dx)
                if not (0 <= cell[0] < agent.size_known and 0 <= cell[1] < agent.size_known): break
                focus.add(("wumpus", cell))
    return focus

def get_possible_actions_now(agent, status_map):
    y, x = agent.location
    actions = []
    direction_moves = {'N': (-1, 0), "S": (1, 0), "W": (0, -1), 'E': (0, 1)}

    if status_map.get(("gold", agent.location)) == "UNSAFE" and not agent.has_gold:
        actions.append("grab")

    if agent.location == agent.start_location:
        actions.append("climb out")
    
    actions.extend(["turn left", "turn right"])

    y, x = agent.location
    dy, dx = direction_moves[agent.direction]
    front_cell = (y + dy, x + dx)
    stench_here = status_map.get(("stench", (y, x)), "UNKNOWN") == "UNSAFE"
    # Search stench at adjacent cells from the past
    neighbors = [(y, x+1), (y+1, x), (y, x-1), (y-1, x)]
    stench_near = any(
        0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known and
        status_map.get(("stench", nb), "UNKNOWN") == "UNSAFE"
        for nb in neighbors
    )
    # Dodge wumpus signal
    urgent_escape = ((len(agent.actions) + 1) % 5 == 0) and (stench_here or stench_near)

    if 0 <= front_cell[0] < agent.size_known and 0 <= front_cell[1] < agent.size_known:
        pit_state = status_map.get(("pit", front_cell), "UNKNOWN")
        w_state   = status_map.get(("wumpus", front_cell), "UNKNOWN")

        if urgent_escape:
            # Move is preferred if it can
            if status_map.get(("wumpus", front_cell), "UNKNOWN") == "UNSAFE" and agent.has_arrow:
                actions.append("shoot")
            elif pit_state != "UNSAFE" and w_state == "SAFE":
                actions.append("move")
            if 'shoot' in actions or 'move' in actions: 
                actions.remove("turn left")
                actions.remove("turn right")
        else:
            if pit_state != "UNSAFE" and w_state != "UNSAFE":
                actions.append("move")

    # Shoot
    w_infront = False
    for i in range(1, agent.size_known):
        nb = (y + i*dy, x + i*dx)
        if not (0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known): break
        if status_map.get(("wumpus", nb), "UNKNOWN") == "UNSAFE":
            w_infront = True
            agent.wumpus_die = nb
            break
    if agent.has_arrow and w_infront:
        actions.append("shoot")

    return actions