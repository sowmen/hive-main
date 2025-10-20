import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import ray
import asyncio
import argparse
import os
from contextlib import asynccontextmanager
from tinydb import TinyDB
from starlette.websockets import WebSocketDisconnect

# Parse arguments before FastAPI app creation
parser = argparse.ArgumentParser(description="Hive Visualizer Server")
parser.add_argument(
    "--json", help="Path to saved graph JSON or TinyDB file", default=None
)
parser.add_argument("--address", help="Ray cluster address", default="auto")
args = parser.parse_args()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if args.json is None:
        session_file = sorted(f for f in os.listdir("sessions") if f.endswith(".json"))[
            -1
        ]
        args.json = os.path.join("sessions", session_file)

    print(f"Using session file: {args.json}")
    app.state.json_path = args.json

    yield

    # Shutdown Ray if it was started
    if ray.is_initialized():
        ray.shutdown()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def retrieve_graph():
    if app.state.json_path and os.path.exists(app.state.json_path):
        db = TinyDB(app.state.json_path)
        all_nodes = db.all()
    else:
        print("[Visualizer] No data source available.")
        return {"nodes": [], "edges": []}

    # Build vis-network nodes/edges
    nodes = []
    edges = []
    color_map = {
        "READY_EXECUTE": "lightblue",
        "RUNNING": "orange",
        "READY_EXPAND": "yellow",
        "EXPANDING": "purple",
        "FINISHED": "lightgreen",
        "NEED_MORE_INFO": "red",
        "GOAL_REACHED": "green",
    }
    for node in all_nodes:
        nodes.append(
            {
                "id": node["id"],
                "label": f"{node['id']}\nState:{node['state']}\nValue:{node.get('value')}",
                "color": color_map.get(node["state"], "gray"),
                "value": (node.get("priority", 0) or 0) * 30 + 10,
            }
        )
        for child in node.get("children", []):
            edges.append({"from": node["id"], "to": child})
    return {"nodes": nodes, "edges": edges}


@app.get("/graph")
async def get_graph():
    return await retrieve_graph()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            nodes_edges = await retrieve_graph()
            await websocket.send_json(nodes_edges)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        print("[Visualizer] WebSocket client disconnected")
    except Exception as e:
        print(f"[Visualizer] Unexpected error in WS loop: {e}")


if __name__ == "__main__":
    uvicorn.run("viz_server:app", host="0.0.0.0", port=8000, ws_ping_timeout=30)
