from definition import Literal
class Agent:
    def __init__(self, num_wumpus=2):
        self.location = (-1, 0)
        self.wumpus_remain = num_wumpus
        self.direction = 'E'
        self.has_gold = False
        self.has_arrow = True
        self.visited = set()
        self.percepts =[] # New percepts at current location
        self.KB = []  # Agent won't know the size of the map until getting bump
    
    def update_direction(self, action):
        directions = ['N', 'E', 'S', 'W']
        current_index = directions.index(self.direction)
        if action == 'turn left':
                new_index = (current_index - 1) % 4
        else:
                new_index = (current_index + 1) % 4
        self.direction = directions[new_index]
    
    def get_KB_from_percepts(self):
        """        Extract knowledge base from agent's percepts
        """
        kb = []
        for percept in self.percepts:
            if isinstance(percept, Literal):
                kb.append([percept])
            else:
                # Handle other percept types if needed
                pass
        self.percepts = []  # Clear percepts after extracting KB
        self.KB.extend(kb)
        
    def extract_symbols(self, kb=None, alpha=None):
        """Extract all propositional symbol keys from KB and alpha"""
        if kb is None:
            kb = self.KB
            
        symbols = set()
        
        # Extract from KB
        for clause in kb:
            for literal in clause:
                symbol_key = f"{literal.name}{literal.pos}"
                symbols.add(symbol_key)
        
        # Extract from alpha if provided
        if alpha is not None:
            if isinstance(alpha, Literal):
                symbol_key = f"{alpha.name}{alpha.pos}"
                symbols.add(symbol_key)
            elif isinstance(alpha, list):
                for literal in alpha:
                    symbol_key = f"{literal.name}{literal.pos}"
                    symbols.add(symbol_key)
        
        return sorted(list(symbols))
    
    def pl_true(self, formula, model):
        """
        PL-TRUE? function - check if formula is true in given model
        """
        if isinstance(formula, Literal):
            # Single literal
            symbol_key = f"{formula.name}{formula.pos}"
            truth_value = model.get(symbol_key, False)
            return not truth_value if formula.negate else truth_value
        
        elif isinstance(formula, list):
            if not formula:
                return True
            
            # Check if it's KB (list of clauses) or single clause
            if isinstance(formula[0], list):
                # KB: List of clauses - all must be true (AND)
                for clause in formula:
                    clause_satisfied = False
                    for literal in clause:
                        symbol_key = f"{literal.name}{literal.pos}"
                        truth_value = model.get(symbol_key, False)
                        literal_true = not truth_value if literal.negate else truth_value
                        if literal_true:
                            clause_satisfied = True
                            break
                    
                    if not clause_satisfied:
                        return False
                return True
            
            elif isinstance(formula[0], Literal):
                # Single clause - at least one literal must be true (OR)
                for literal in formula:
                    symbol_key = f"{literal.name}{literal.pos}"
                    truth_value = model.get(symbol_key, False)
                    literal_true = not truth_value if literal.negate else truth_value
                    if literal_true:
                        return True
                return False
        
        return False
    
    def tt_check_all(self, kb, alpha, symbols, model):
        """
        TT-CHECK-ALL: Recursively check all possible truth assignments
        """
        # Base case: all symbols assigned
        if not symbols:
            if self.pl_true(kb, model):
                return self.pl_true(alpha, model)
            else:
                return True  # Vacuous truth when KB is false
        
        # Recursive case
        p = symbols[0]
        rest = symbols[1:]
        
        # Try p = True
        model_true = model.copy()
        model_true[p] = True
        
        # Try p = False  
        model_false = model.copy()
        model_false[p] = False
        
        return (self.tt_check_all(kb, alpha, rest, model_true) and 
                self.tt_check_all(kb, alpha, rest, model_false))
    
    def tt_entails(self, alpha, kb=None):
        """
        TT-ENTAILS: Check if KB entails alpha
        
        Args:
            alpha: Query literal to check
            kb: Knowledge base (defaults to self.KB)
        """
        if kb is None:
            kb = self.KB
            
        if not kb:  # Empty KB entails nothing
            return False
            
        symbols = self.extract_symbols(kb, alpha)
        return self.tt_check_all(kb, alpha, symbols, {})
    
    def add_to_kb(self, clause):
        """
        Add a clause to the knowledge base
        
        Args:
            clause: List of literals or single literal
        """
        if isinstance(clause, Literal):
            clause = [clause]
        self.KB.append(clause)
    
    def infer_new_knowledge(self):
        """
        Use TT-ENTAILS to infer new literals from current KB
        Returns list of entailed literals not already in KB
        """
        if not self.KB:
            return []
        
        symbols = self.extract_symbols(self.KB)
        entailed_literals = []
        
        # Check all possible literals for entailment
        for symbol in symbols:
            # Parse symbol to extract name and position
            # Simplified parsing - assumes format like "P(1,2)"
            name = symbol[0]  # First character is the name
            pos_str = symbol[1:]  # Rest is position
            
            # Try to parse position - handle both (x,y) and simple formats
            try:
                if '(' in pos_str:
                    pos_clean = pos_str.strip('()')
                    if ',' in pos_clean:
                        parts = pos_clean.split(',')
                        pos = (int(parts[0]), int(parts[1]))
                    else:
                        pos = (int(pos_clean),)
                else:
                    # Simple format like "P12" -> extract numbers
                    numbers = ''.join([c for c in pos_str if c.isdigit()])
                    if len(numbers) >= 2:
                        pos = (int(numbers[0]), int(numbers[1]))
                    else:
                        pos = (int(numbers),) if numbers else (1, 1)
            except:
                pos = (1, 1)  # Default fallback
            
            # Test positive literal
            positive_lit = Literal(name, pos, False)
            if self.tt_entails(positive_lit) and not self._is_literal_in_kb(positive_lit):
                entailed_literals.append(positive_lit)
            
            # Test negative literal
            negative_lit = Literal(name, pos, True)  
            if self.tt_entails(negative_lit) and not self._is_literal_in_kb(negative_lit):
                entailed_literals.append(negative_lit)
        
        return entailed_literals
    
    def _is_literal_in_kb(self, literal):
        """Check if a literal is already explicitly stated in KB"""
        for clause in self.KB:
            if len(clause) == 1 and clause[0] == literal:
                return True
        return False
    
    def is_safe(self, position):
        """
        Check if a position is safe based on current knowledge
        A position is safe if KB entails ¬Pit(x,y) and ¬Wumpus(x,y)
        """
        pit_literal = Literal('pit', position, True)    # ¬P(x,y)
        wumpus_literal = Literal('wumpus', position, True) # ¬W(x,y)
        
        return (self.tt_entails(pit_literal) and 
                self.tt_entails(wumpus_literal))
    
    def is_dangerous(self, position):
        """
        Check if a position is definitely dangerous
        A position is dangerous if KB entails Pit(x,y) or Wumpus(x,y)
        """
        pit_literal = Literal('pit', position, False)    # P(x,y)
        wumpus_literal = Literal('wumpus', position, False) # W(x,y)
        
        return (self.tt_entails(pit_literal) or 
                self.tt_entails(wumpus_literal))
    
    def get_safe_unvisited_positions(self, max_x=4, max_y=4):
        """
        Get all positions that are safe and unvisited
        """
        safe_positions = []
        for x in range(max_x):
            for y in range(max_y):
                pos = (x, y)
                if pos not in self.visited and self.is_safe(pos):
                    safe_positions.append(pos)
        return safe_positions
    
    def update_kb_with_percepts(self, percepts, position=None):
        """
        Update KB based on percepts at current or given position
        
        Args:
            percepts: Dictionary with keys like 'breeze', 'stench', 'glitter', 'bump', 'scream'
            position: Position where percepts were observed (defaults to current location)
        """
        if position is None:
            position = self.location
        
        # Add percept information to KB
        if percepts.get('breeze', False):
            # There's a breeze, so there's a pit nearby
            breeze_literal = Literal('B', position, False)  # B(x,y)
            self.add_to_kb([breeze_literal])
        else:
            # No breeze, so no pit nearby
            no_breeze_literal = Literal('B', position, True)  # ¬B(x,y)
            self.add_to_kb([no_breeze_literal])
        
        if percepts.get('stench', False):
            # There's a stench, so wumpus is nearby
            stench_literal = Literal('S', position, False)  # S(x,y)
            self.add_to_kb([stench_literal])
        else:
            # No stench, so no wumpus nearby
            no_stench_literal = Literal('S', position, True)  # ¬S(x,y)
            self.add_to_kb([no_stench_literal])
        
        # Add rule: if no breeze at (x,y), then no pits in adjacent cells
        if not percepts.get('breeze', False):
            adjacent_positions = self._get_adjacent_positions(position)
            for adj_pos in adjacent_positions:
                no_pit_literal = Literal('P', adj_pos, True)  # ¬P(adj_x, adj_y)
                self.add_to_kb([no_pit_literal])
        
        # Add rule: if no stench at (x,y), then no wumpus in adjacent cells  
        if not percepts.get('stench', False):
            adjacent_positions = self._get_adjacent_positions(position)
            for adj_pos in adjacent_positions:
                no_wumpus_literal = Literal('W', adj_pos, True)  # ¬W(adj_x, adj_y)
                self.add_to_kb([no_wumpus_literal])
    
    def _get_adjacent_positions(self, position):
        """Get valid adjacent positions"""
        x, y = position
        adjacent = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if new_x >= 0 and new_y >= 0:  # Assuming non-negative coordinates
                adjacent.append((new_x, new_y))
        return adjacent
    
    def print_kb(self):
        """Print current knowledge base in readable format"""
        print("=== Agent's Knowledge Base ===")
        if not self.KB:
            print("KB is empty")
            return
            
        for i, clause in enumerate(self.KB):
            clause_str = " ∨ ".join([str(lit) for lit in clause])
            print(f"Clause {i+1}: {clause_str}")
    
    def print_inferences(self):
        """Print what the agent can infer from current KB"""
        print("=== Agent's Inferences ===")
        inferred = self.infer_new_knowledge()
        if inferred:
            for lit in inferred:
                print(f"Can infer: {lit}")
        else:
            print("No new inferences available")


# Example usage and testing
def test_agent_reasoning():
    """Test the agent's reasoning capabilities"""
    agent = Agent()
    
    print("=== Testing Agent Knowledge Base Reasoning ===\n")
    
    # Simulate agent's knowledge from your example
    print("Adding knowledge to agent's KB...")
    
    # Add clauses from your example
    agent.add_to_kb([Literal('P', (1,2), True)])  # ¬P(1,2)
    agent.add_to_kb([Literal('B', (1,1), True), Literal('P',(1,2), False), Literal('P',(2,1), False)])
    agent.add_to_kb([Literal('P',(1,2), True), Literal('B',(1,1), False)])
    agent.add_to_kb([Literal('P',(2,1), True), Literal('B', (1,1), False)])
    agent.add_to_kb([Literal('B', (1,1), False)])  # B(1,1)
    
    agent.print_kb()
    print()
    
    # Test specific queries
    print("=== Testing Agent's Reasoning ===")
    
    queries = [
        Literal('P', (2,1), True),   # ¬P(2,1)  
        Literal('P', (2,1), False),  # P(2,1)
        Literal('B', (1,1), False),  # B(1,1)
        Literal('B', (1,1), True)    # ¬B(1,1)
    ]
    
    for query in queries:
        result = agent.tt_entails(query)
        print(f"Agent knows {query}? {result}")
    
    print()
    agent.print_inferences()
    
    print("\n=== Testing Safety Reasoning ===")
    
    # Test safety of positions
    positions_to_check = [(1,2), (2,1), (0,1), (1,0)]
    for pos in positions_to_check:
        safe = agent.is_safe(pos)
        dangerous = agent.is_dangerous(pos)
        print(f"Position {pos}: Safe={safe}, Dangerous={dangerous}")
    
    print("\n=== Simulating Percept Updates ===")
    
    # Simulate agent receiving percepts
    agent.location = (0, 0)
    percepts = {'breeze': False, 'stench': False}
    agent.update_kb_with_percepts(percepts)
    
    print("After receiving percepts at (0,0) - no breeze, no stench:")
    agent.print_kb()


if __name__ == "__main__":
    test_agent_reasoning()
