def forward_chaining(kb, known):
    added = True
    while added:
        added = False
        for rule in kb:
            if all(cond in known for cond in rule.conditions):
                if rule.conclusion not in known:
                    known.add(rule.conclusion)
                    added = True
                    print(f"Inferred: {rule.conclusion}")
    return known