import ray


@ray.remote
class PlannerActor:
    def __init__(self, db_actor):
        self.db_actor = db_actor
        print(f"[Planner] Initialized")

    def expand_node(self, node_id):
        node: dict = ray.get(self.db_actor.search.remote(lambda n: n["id"] == node_id))[0]
        if not node:
            print(f"[Planner] Node {node_id} not found.")
            return

        print(f"[Planner] Expanding node {node_id}...")

        # TODO: Simulated idea generation — replace with LLM integration
        ideas = [f"Optimization idea {i} from {node_id}" for i in range(1, 4)]

        # Insert children into DB
        for idea in ideas:
            new_id = f"{node_id}_child_{abs(hash(idea)) % 9999}"
            child_task = {
                "id": new_id,
                "state": "READY_EXECUTE",
                "priority": 0.5,
                "value": None,
                "depth": (node.get("depth", 0) + 1),
                "metadata": {"idea": idea},
                "children": [],
                "parent": node_id,
            }
            self.db_actor.insert_node.remote(child_task)
            node["children"].append(new_id)

        # Mark node as expanded / finished
        self.db_actor.update_node.remote(
            node_id, {"state": "FINISHED", "children": node["children"]}
        )
        print(
            f"[Planner] Finished expanding node {node_id}. Added {len(ideas)} children."
        )
