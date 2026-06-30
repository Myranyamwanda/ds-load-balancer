from fastapi import FastAPI, HTTPException  # type: ignore[reportMissingImports]
from pydantic import BaseModel, Field  # type: ignore[reportMissingImports]
import asyncio
import httpx  # type: ignore[reportMissingImports]
import random

from consistent_hash import ConsistentHash
from replica_manager import ReplicaManager
from health_monitor import monitor


app = FastAPI()

replicas = ReplicaManager()

hash_ring = ConsistentHash()


# ==========================
# Request Models
# ==========================

class AddRequest(BaseModel):

    n: int
    hostnames: list[str] = Field(default_factory=list)


class RemoveRequest(BaseModel):

    n: int
    hostnames: list[str] = Field(default_factory=list)


# ==========================
# Startup Initialization
# ==========================

@app.on_event("startup")
async def startup():

    # Create default N=3 replicas

    for i in range(3):

        hostname = f"server{i}"

        replicas.spawn(
            hostname
        )

        hash_ring.add_server(
            hostname
        )

    # Start heartbeat monitor in background

    asyncio.create_task(

        monitor(
            replicas,
            hash_ring
        )
    )


# ==========================
# GET /rep
# Return active replicas
# ==========================

@app.get("/rep")
async def get_replicas():

    return {

        "replicas":
        list(
            replicas.active_servers.keys()
        )

    }


# ==========================
# POST /add
# Add server replicas
# ==========================

@app.post("/add")
async def add_servers(
        req: AddRequest
):

    names = req.hostnames.copy()

    if len(names) > req.n:

        raise HTTPException(
            status_code=400,
            detail="hostname list exceeds n"
        )

    # Generate random names if needed

    while len(names) < req.n:

        names.append(
            replicas.generate_hostname()
        )

    added=[]

    for hostname in names:

        replicas.spawn(
            hostname
        )

        hash_ring.add_server(
            hostname
        )

        added.append(
            hostname
        )

    return {

        "message":
        "servers added",

        "added":
        added,

        "replicas":
        list(
            replicas.active_servers.keys()
        )
    }


# ==========================
# DELETE /rm
# Remove replicas
# ==========================

@app.delete("/rm")
async def remove_servers(
        req: RemoveRequest
):

    names=req.hostnames.copy()

    if len(names)>req.n:

        raise HTTPException(
            status_code=400,
            detail="hostname list exceeds n"
        )

    selected=names.copy()


    while len(selected)<req.n:

        random_server=random.choice(

            list(
                replicas.active_servers.keys()
            )
        )

        if random_server not in selected:

            selected.append(
                random_server
            )


    removed=[]

    for hostname in selected:

        replicas.remove(
            hostname
        )

        hash_ring.remove_server(
            hostname
        )

        removed.append(
            hostname
        )



    return {

        "message":
        "servers removed",

        "removed":
        removed,

        "replicas":
        list(
            replicas.active_servers.keys()
        )
    }


# ==========================
# Route incoming requests
# GET /<path>
# ==========================

@app.get("/{path:path}")
async def route_request(
        path:str
):

    request_id=random.randint(
        1,
        100000
    )

    server=hash_ring.get_server(
        request_id
    )

    if not server:

        raise HTTPException(
            status_code=500,
            detail="No active servers"
        )


    port = replicas.get_port(
        server
    )

    url = f"http://localhost:{port}/{path}"

    async with httpx.AsyncClient() as client:

        try:

            response=await client.get(
                url
            )

            return response.json()

        except Exception as e:

            print(e)

            raise HTTPException(
                status_code=500,
                detail="Failed to route request"
            )


# ==========================
# Run Server
# ==========================

if __name__=="__main__":

    import uvicorn  # pyright: ignore[reportMissingImports]

    uvicorn.run(
        "load_balancer:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
