from src.session_manager import SessionManager
from src.graph_utils import load_graph_from_db, visualize_graph

sm = SessionManager()
sessions = sm.list_sessions()
if not sessions:
    print("No sessions found.")
else:
    # Load the first session found
    session_id = sessions[-1]
    db = sm.load_session(session_id)
    G = load_graph_from_db(db)
    visualize_graph(G, output_file=f"{session_id}_graph.html")