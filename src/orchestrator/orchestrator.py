import ray


@ray.remote
class OrchestratorActor:
    def __init__(self, db_actor, worker_pool=None, planner_actor=None):
        """
        db_actor: DB_Actor handle for TinyDB
        worker_pool: list of WorkerActor references
        planner_actor: PlannerActor reference
        """
        self.db_actor = db_actor
        self.worker_pool = worker_pool or []
        self.planner_actor = planner_actor
        print(f"[Orchestrator] Initialized")

    def scan_and_dispatch(self, iter):
        """
        Handle both READY_EXECUTE and READY_EXPAND queues.
        """

        # ---- Worker-ready nodes ----
        ready_exec = ray.get(self.db_actor.get_nodes.remote("READY_EXECUTE"))
        ready_exec.sort(key=lambda t: t.get("priority", 0.0), reverse=True)

        if ready_exec:
            print(
                f"[Orchestrator (iter:{iter})] Dispatching {len(ready_exec)} tasks to workers."
            )
            for idx, node in enumerate(ready_exec):
                if not self.worker_pool:
                    print(
                        f"[Orchestrator (iter:{iter})] No workers available for node {node['id']}"
                    )
                    continue
                worker = self.worker_pool[idx % len(self.worker_pool)]
                print(
                    f"[Orchestrator (iter:{iter})] Assigning task {node['id']} to worker {idx % len(self.worker_pool)}"
                )
                ray.get(
                    self.db_actor.update_node.remote(node["id"], {"state": "RUNNING"})
                )
                worker.run_task.remote(node["id"])

        # ---- Planner-ready nodes ----
        ready_expand = ray.get(self.db_actor.get_nodes.remote("READY_EXPAND"))
        print(
            f"[Orchestrator (iter:{iter})] Found {len(ready_expand)} nodes ready to expand"
        )
        if ready_expand:
            chosen_nodes = self.select_nodes_for_expansion(ready_expand)
            for node in chosen_nodes:
                print(
                    f"[Orchestrator (iter:{iter})] Sending node {node['id']} to Planner."
                )
                ray.get(
                    self.db_actor.update_node.remote(node["id"], {"state": "EXPANDING"})
                )
                self.planner_actor.expand_node.remote(node["id"])

    def select_nodes_for_expansion(self, candidates):
        """
        Select nodes for expansion.
        Here: simple heuristic — highest value first.
        Later: plug in MCTS.
        """
        if not candidates:
            return []
        # For root, just pick it directly
        root_nodes = [n for n in candidates if n["id"] == "root"]
        if root_nodes:
            return root_nodes
        # Else, choose best value node
        return sorted(candidates, key=lambda t: t.get("value", 0.0), reverse=True)[:1]

    def handle_need_info(self, iter):
        need_info_nodes = ray.get(self.db_actor.get_nodes.remote("NEED_MORE_INFO"))
        for node in need_info_nodes:
            # Mark state as ticket sent
            # TODO: Might need to be immediate
            self.db_actor.update_node.remote(node["id"], {"state": "TICKET_SENT"})

            # Push ticket (real system would send to external service)
            # TODO
            print(
                f"[Ticket] node {node['id']} needs info: {node['metadata'].get('info_required', 'N/A')}"
            )

        print(f"[Orchestrator (iter:{iter})] Sent {len(need_info_nodes)} tickets.")

    def restart_session(self):
        running_nodes = ray.get(self.db_actor.get_nodes.remote("RUNNING"))
        for node in running_nodes:
            self.db_actor.update_node.remote(node["id"], {"state": "READY_EXECUTE"})
        print(
            f"[Orchestrator] Reset {len(running_nodes)} RUNNING nodes to READY_EXECUTE."
        )
