To run optimization run:
```
python main.py

# Arguments:
--restart: Will restart the last session
--data_path: Path to the folder containing the data files for optimization
--num_worker: Number of parallel ray workers
```

To view the current optimization graph, in a new terminal run, and open the link in the browser:
```
python viz_server.py
```

## State Definition

|State|Meaning|Who handles it|
| -------- | ------- | ------- |
|READY_EXECUTE|Ready to be processed by a Worker to produce result/value|WorkerActor|
RUNNING|Currently being processed by a Worker|WorkerActor|
FINISHED|Worker done, value is stored|PlannerAgent|
READY_EXPAND|Ready to be expanded into subtasks/ideas|PlannerActor|
EXPANDING|Currently being expanded by Planner|PlannerActor|
NEED_MORE_INFO|Missing info from user|Orchestrator|
FAILED|Task failed|Orchestrator|
GOAL_REACHED|Objective was completed|N/A|
