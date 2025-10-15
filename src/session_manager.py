import os
from datetime import datetime
from tinydb import TinyDB

class SessionManager:
    def __init__(self, base_dir="sessions"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def create_session(self, user_id):
        """
        Create a new session JSON file and return TinyDB instance + session_id.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{user_id}_{ts}"
        session_path = self.get_session_file_path(session_id)
        return session_id, session_path

    def load_session(self, session_id):
        """
        Load existing session TinyDB instance.
        """
        session_path = self.get_session_file_path(session_id)
        if not os.path.exists(session_path):
            raise FileNotFoundError(f"Session {session_id} does not exist.")
        return session_path

    def list_sessions(self):
        """
        List existing session files.
        """
        return [f[:-5] for f in os.listdir(self.base_dir) if f.endswith(".json")]
    
    def get_session_file_path(self, session_id):
        return os.path.join(self.base_dir, f"{session_id}.json")