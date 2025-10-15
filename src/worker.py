import ray
import time

from .value_fn_base import ValueFunction


@ray.remote
class WorkerActor:
    def __init__(self, db_actor, max_depth, expand_threshold, value_fn: ValueFunction):
        self.db_actor = db_actor
        self.max_depth = max_depth
        self.expand_threshold = expand_threshold
        self.value_fn = value_fn
        print(f"[Worker] Initialized")

    def run_task(self, node_id):
        print(f"[Worker] Starting task: {node_id}")

        # TODO: Simulate work (e.g., compile RTL and get PPA)
        time.sleep(5)
        ppa_report = {"performance_mhz": 500, "power_mw": 32, "area_mm2": 1.5}

        try:
            fake_value = self.value_fn.validate_return(self.value_fn(ppa_report))
        except (TypeError, ValueError) as e:
            print(f"[Worker] ValueFunction error for node {task_id}: {e}")
            fake_value = -float("inf")  # or handle as FAILED
        # fake_value = round(abs(hash(node_id)) % 1000 / 10.0, 2)  # simulated score

        # Fetch current depth to decide end state
        node = ray.get(self.db_actor.search.remote(lambda x: x["id"] == node_id))[0]
        depth = node.get("depth", 0)

        if (self.max_depth and depth >= self.max_depth) or (
            self.expand_threshold and fake_value < self.expand_threshold
        ):
            next_state = "FINISHED"
        else:
            next_state = "READY_EXPAND"

        # Mark finished in DB
        self.db_actor.update_node.remote(
            node_id, {"state": next_state, "value": fake_value}
        )
        print(f"[Worker] Task {node_id} done, value={fake_value}, state={next_state}")
