from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import asyncio
import httpx
import random

from consistent_hash import ConsistentHash
from replica_manager import ReplicaManager
from health_monitor import monitor


app = FastAPI()
replicas = ReplicaManager()
hash_ring = ConsistentHash()


class AddRequest(BaseModel):
    n: int
    hostnames: list[str] = Field(default_factory=list)


class RemoveRequest(BaseModel):
    n: int
    hostnames: list[str] = Field(default_factory=list)


@app.on_event("startup")
async def startup():
    for i in range(3):
        hostname = f"server{i}"
        replicas.spawn(hostname)
        hash_ring.add_server(hostname)

    asyncio.create_task(monitor(replicas, hash_ring))


@app.get("/rep")
async def get_replicas():
    return {"replicas": list(replicas.active_servers.keys())}


@app.post("/add")
async def add_servers(req: AddRequest):
    names = req.hostnames.copy()

    if len(names) > req.n:
        raise HTTPException(status_code=400, detail="hostname list exceeds n")

    while len(names) < req.n:
        names.append(replicas.generate_hostname())

    added = []
    for hostname in names:
        replicas.spawn(hostname)
        hash_ring.add_server(hostname)
        added.append(hostname)

    return {
        "message": "servers added",
        "added": added,
        "replicas": list(replicas.active_servers.keys()),
    }


@app.delete("/rm")
async def remove_servers(req: RemoveRequest):
    names = req.hostnames.copy()

    if len(names) > req.n:
        raise HTTPException(status_code=400, detail="hostname list exceeds n")

    selected = names.copy()
    while len(selected) < req.n:
        random_server = random.choice(list(replicas.active_servers.keys()))
        if random_server not in selected:
            selected.append(random_server)

    removed = []
    for hostname in selected:
        replicas.remove(hostname)
        hash_ring.remove_server(hostname)
        removed.append(hostname)

    return {
        "message": "servers removed",
        "removed": removed,
        "replicas": list(replicas.active_servers.keys()),
    }


@app.get("/{path:path}")
async def route_request(path: str):
    request_id = random.randint(1, 100000)
    server = hash_ring.get_server(request_id)

    if not server:
        raise HTTPException(status_code=500, detail="No active servers")

    url = f"http://{server}:5000/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            return response.json()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Failed to route request")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("load_balancer:app", host="0.0.0.0", port=5000, reload=True)