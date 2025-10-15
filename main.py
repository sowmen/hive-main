import ray
import time
import argparse
import yaml

from src.session_manager import SessionManager
from src.session_input import create_input
from src.planner import PlannerActor
from src.orchestrator import OrchestratorActor
from src.worker import WorkerActor
from src.db_actor import DBActor
from src.utils import redirect_print_to_log

from value_fn import DefinedValueFunction

if __name__ == "__main__":
    import debugpy

    # debugpy.listen(5678)
    # print("Waiting for debugger attach")
    # debugpy.wait_for_client()
    # debugpy.breakpoint()
    # print('break on this line')

    # redirect_print_to_log("log.txt")
    ray.init(runtime_env={"env_vars": {"RAY_DEBUG": "legacy"}})

    parser = argparse.ArgumentParser()
    parser.add_argument("--restart", help="Continue last session", action="store_true")
    parser.add_argument("--num_worker", help="Number of workers", type=int, default=3)
    parser.add_argument(
        "--config",
        help="Path to the optimization config file",
        default="test_data/optimization_config.yaml",
    )
    args = parser.parse_args()

    # Load the optimization config
    with open(args.config, "r") as fp:
        config = yaml.safe_load(fp)["exploration"]

    OBJECTIVE_VALUE_THRESHOLD = config["objective_value_threshold"]
    LOOP_SLEEP_SEC = config["loop_sleep_sec"]
    MAX_TREE_DEPTH = config["max_tree_depth"]
    EXPAND_THRESHOLD = config["expand_threshold"]

    sm = SessionManager()

    if args.restart:
        # Load the last session
        session_id = sm.list_sessions()[-1]
        db_path = sm.load_session(session_id)
        print(f"[INFO] Loaded session: {session_id} from {db_path}")

        db_actor = DBActor.remote(db_path)
    else:
        # Create a new session
        session_id, db_path = sm.create_session(user_id="test")
        print(f"[INFO] Created new session: {session_id} under {db_path}")

    # ==== Create planner + workers ====
    value_fn = DefinedValueFunction()
    db_actor = DBActor.options(name="db_actor").remote(db_path)
    planner = PlannerActor.options(name="planner_actor").remote(db_actor)
    workers = [
        WorkerActor.remote(db_actor, MAX_TREE_DEPTH, EXPAND_THRESHOLD, value_fn)
        for _ in range(args.num_worker)
    ]
    orch = OrchestratorActor.options(name="orch_actor").remote(
        db_actor, worker_pool=workers, planner_actor=planner
    )

    if args.restart:
        # Check for unfinished tasks from previous session
        orch.restart_session.remote()
    else:
        # Insert root node
        root_metadata = create_input(data_path="test_data")
        ray.get(
            db_actor.insert_node.remote(
                {
                    "id": "root",
                    "state": "READY_EXPAND",
                    "priority": 0.0,
                    "value": None,
                    "depth": 0,
                    "metadata": root_metadata.to_dict(),
                    "children": [],  # list of child node IDs
                    "parent": None,
                }
            )
        )

    try:
        iter = 0
        while True:
            iter += 1

            # Orchestrator decides work allocation
            orch.handle_need_info.remote(iter)
            orch.scan_and_dispatch.remote(iter)

            all_nodes = ray.get(db_actor.get_all.remote())

            # ---- Objective check ----
            finished_nodes = [
                node
                for node in all_nodes
                if (node["state"] == "FINISHED" or node["state"] == "READY_EXPAND")
            ]
            for node in finished_nodes:
                if (
                    node["value"] is not None
                    and node["value"] >= OBJECTIVE_VALUE_THRESHOLD
                ):
                    print(
                        f"[MAIN] Objective achieved by node {node['id']} (value={node['value']})"
                    )
                    raise KeyboardInterrupt

            # 1. Check for ready to dispatch nodes
            ready_execute_nodes = [
                node for node in all_nodes if node["state"] == "READY_EXECUTE"
            ]

            # 2. Check for ready to expand nodes
            ready_expand_nodes_below_max_depth = [
                node
                for node in all_nodes
                if (node["state"] == "READY_EXPAND") and node["depth"] < MAX_TREE_DEPTH
            ]

            # 3. Check for active nodes
            active_nodes = [
                node
                for node in all_nodes
                if node["state"] == "RUNNING" or node["state"] == "EXPANDING"
            ]

            if (
                not active_nodes
                and not ready_execute_nodes
                and not ready_expand_nodes_below_max_depth
            ):
                print(f"[MAIN] No active nodes and no nodes to expand. Stopping.")
                break

            time.sleep(LOOP_SLEEP_SEC)

    except KeyboardInterrupt:
        print("[MAIN] Stopping due to interrupt.")

    # End of main loop
    print("[MAIN] Session ended.")
