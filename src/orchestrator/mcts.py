def run_mcts(graph_snapshot):
    # Simplified UCT-like selection
    ready_nodes = [n['t'] for n in graph_snapshot if n['t']['state'] == 'READY']
    # Here: apply MCTS scoring
    ordered = sorted(ready_nodes, key=lambda x: x.get('priority', 0), reverse=True)
    return [n['id'] for n in ordered]