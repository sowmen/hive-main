import ray
from tinydb import TinyDB, Query


@ray.remote
class DBActor:
    def __init__(self, file_path):
        """
        Initialize TinyDB storage inside a dedicated Actor process.
        """
        self.file_path = file_path
        self.db = TinyDB(file_path)

    def insert_node(self, node):
        """
        Insert a node document into DB.
        """
        self.db.insert(node)

    def get_nodes(self, state):
        """
        Search by state.
        """
        Node = Query()
        return self.db.search(Node.state == state)

    def search(self, filter_fn):
        """
        Return all nodes with a given condition.
        """
        return self.db.search(filter_fn)

    def update_node(self, node_id, updates: dict):
        """
        Update a node given its ID.
        """
        node = Query()
        self.db.update(updates, node.id == node_id)

    def get_all(self):
        """
        Dump all nodes for visualization or inspection.
        """
        return self.db.all()
