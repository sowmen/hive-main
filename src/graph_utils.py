import json
import networkx as nx
from pyvis.network import Network

def load_graph_from_db(db):
    """
    Load TinyDB data into a NetworkX directed graph.
    """
    G = nx.DiGraph()
    for task in db.all():
        G.add_node(task['id'], **task)
        # Add children (edges) only if they exist in DB
        for child in task.get('edges', []):
            # Add edge in NX; if child isn't yet in G, add node placeholder
            if not G.has_node(child):
                G.add_node(child, state="UNKNOWN", priority=0, value=None, depth=None, metadata={})
            G.add_edge(task['id'], child)
    return G

def visualize_graph(G, output_file="graph.html", hierarchical=True):
    """
    Create HTML interactive visualization using PyVis.
    If hierarchical=True, render as a tree.
    """
    net = Network(height="750px", width="100%", directed=True)

    if hierarchical:
        net.set_options("""var options = {
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "UD",
                    "sortMethod": "directed"
                }
            },
            "physics": {
                "hierarchicalRepulsion": {
                    "nodeDistance": 120
                },
                "minVelocity": 0.75
            }
        }""")

    for node, data in G.nodes(data=True):
        label = f"{node}\nState: {data.get('state')}\nPriority: {data.get('priority')}\nValue: {data.get('value')}"
        color = {
            "READY": "lightblue",
            "RUNNING": "orange",
            "FINISHED": "lightgreen",
            "NEED_MORE_INFO": "red",
            "UNKNOWN": "gray"
        }.get(data.get('state'), "gray")
        # scale size based on priority
        size = (data.get('priority') or 0) * 30 + 15
        net.add_node(
            node,
            label=label,
            color=color,
            size=size,
            title=json.dumps(data.get('metadata', {}), indent=2)
        )

    # Add edges from NX
    for src, dst in G.edges():
        net.add_edge(src, dst)

    net.write_html(output_file, notebook=False)
    print(f"[INFO] Graph visualization saved to {output_file}")