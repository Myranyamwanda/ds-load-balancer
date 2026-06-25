# Distributed Systems: Customizable Load Balancer

## 1. Project Overview
This project implements a customizable load balancer that asynchronously manages and distributes client requests across multiple containerized server replicas using a consistent hashing algorithm. The primary goal is to maintain a scalable, fault-tolerant cluster (maintaining $N=3$ default server instances) capable of dynamically adjusting to load demands and recovering from single-point-of-failure server crashes.


## 2. System Architecture & Components

### Task 1: Server Replicas (`/home`, `/heartbeat`)
Each backend server runs inside a Docker container using a lightweight Python-Flask framework listening on internal port `5000`. 
* `GET /home`: Returns a JSON object identifying the active container: `{"message": "Hello from Server: <SERVER_ID>", "status": "successful"}`.
* `GET /heartbeat`: Returns an empty HTTP 200 payload used explicitly by the load balancer for health monitoring.


### Task 2: Consistent Hash Map (To be completed by Team)
A custom data structure designed to prevent massive cache-miss reshuffles. It maps $N=3$ physical servers across virtual slots using a configuration of:
* Total Slots: `512`
* Virtual Replicas per Server ($K$): `9`
* Custom mathematical mapping hashes request IDs to server nodes cleanly.

### Task 3: Load Balancer (To be completed by Team)
The primary entryway handling endpoints such as `/rep`, `/add`, and `/rm` to scale instances, routing all incoming client data to active nodes on the `net1` network network interface.

---

## 3. Directory Structure
```text
ds-load-balancer/
├── server.py              # Task 1: Flask web server implementation
├── Dockerfile             # Task 1: Container configuration file
├── requirements.txt       # Python dependency tracking (Flask)
├── README.md              # Project documentation and guide
└── .gitignore             # Ignored tracking data (__pycache__/)
