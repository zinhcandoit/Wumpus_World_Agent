def make_clause(literals):
            """Canonicalize clause -> frozenset; drop tautologies (A and ¬A)."""
            s = set(literals)
            # drop tautology: if a (name,pos) appears with both negate True/False -> ignore
            for name_pos in {(lit.name, lit.pos) for lit in s}:
                negs = {lit.negate for lit in s if (lit.name, lit.pos) == name_pos}
                if len(negs) > 1:
                    return None
            return frozenset(s)
def _symbols_from_KB(KB):
    """Return ordered list of propositional symbols as tuples (name,pos)."""
    vars_set = set()
    for clause in KB:
        for lit in clause:
            vars_set.add((lit.name, lit.pos))
    # deterministic order
    return sorted(vars_set, key=lambda t: (t[0], t[1]))

def _pl_true_literal(literal, model):
    """Evaluate a literal under (complete) model dict var->bool."""
    var = (literal.name, literal.pos)
    val = model.get(var, False)  # if not present, default False (but should be complete)
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
        var = (lit.name, lit.pos)
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
    alpha_var = (alpha_literal.name, alpha_literal.pos)
    if alpha_var not in symbols:
        symbols = symbols + [alpha_var]
    return _tt_check_all(KB, alpha_literal, symbols, {})


def classify_all_literals(KB):
    """
    For every var (name,pos) in KB, determine:
      - "UNSAFE" if KB |= (name,pos)  (i.e. entails positive literal)
      - "SAFE"   if KB |= ¬(name,pos)
      - "UNKNOWN" otherwise
    Returns dict mapping (name,pos) -> state.
    """
    result = {}
    symbols = _symbols_from_KB(KB)
    # pick a Literal class from KB to construct new Literal objects
    if not KB:
        return result
    sample_lit = next(iter(next(iter(KB))))
    LitType = type(sample_lit)

    for var in symbols:
        name, pos = var
        pos = tuple(pos)
        pos_name = (name, pos)
        pos_lit = LitType(name, pos, False)
        neg_lit = LitType(name, pos, True)

        entails_pos = tt_entails(KB, pos_lit)
        if entails_pos:
            result[pos_name] = "UNSAFE"
            continue
        entails_neg = tt_entails(KB, neg_lit)
        if entails_neg:
            result[pos_name] = "SAFE"
        else:
            result[pos_name] = "UNKNOWN"
    return result
def get_possible_actions(agent, cell_states:dict):
    """
    Xác định danh sách hành động có thể làm dựa trên trạng thái agent và thông tin safe/unsafe.
    
    Parameters:
    - agent: object có các thuộc tính:
        location (tuple): (y,x) hiện tại
        direction (str): 'N', 'S', 'E', 'W'
        has_gold (bool)
        has_arrow (bool)
        start_location (tuple)
    - cell_states: dict {("pit",(y,x)): "SAFE"/"UNSAFE"/"UNKNOWN", ("wumpus",(y,x)): ...}

    Returns:
    - List[str]: danh sách hành động có thể làm
    """
    actions = []

    # Bảng vector di chuyển
    direction_moves = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}

    # 2. move: chỉ nếu ô trước mặt là SAFE
    dy, dx = direction_moves[agent.direction]
    front_cell = (agent.location[0] + dy, agent.location[1] + dx)
    if 0 <= front_cell[0] < agent.size_known and 0 <= front_cell[1] < agent.size_known:
        pit_state = cell_states.get(("pit", front_cell), "UNKNOWN")
        wumpus_state = cell_states.get(("wumpus", front_cell), "UNKNOWN")
        if pit_state != "UNSAFE" and wumpus_state != "UNSAFE":
            actions.append("move")

    # 2. shoot: nếu chắc chắn có wumpus trước mặt và còn tên
    # Kiểm tra: Cập nhật facing có xảy ra trước không?
    wumpus_infront = False
    for i in range(1, agent.size_known):
        nb = (agent.location[0] + i * dy, agent.location[1] + i * dx)
        if not (0 <= nb[0] < agent.size_known and 0 <= nb[1] < agent.size_known):
            break  # out of bounds
        wumpus_infront = True if cell_states.get(("wumpus", front_cell), "UNKNOWN") == "UNSAFE" else False
    if agent.has_arrow and wumpus_infront:
        actions.append("shoot")

    # 3. turn left / turn right: luôn hợp lệ
    actions.extend(["turn left", "turn right"])

    # 4. grab: nếu có vàng tại vị trí hiện tại
    if ("gold", agent.location) in cell_states and cell_states[("gold", agent.location)] == "UNSAFE" and agent.has_gold == False:
        # Ở đây "UNSAFE" nghĩa là chắc chắn có gold
        actions.append("grab")

    # 5. climb out: nếu ở ô xuất phát
    if agent.location == agent.start_location:
        actions.append("climb out")

    return actions

