# Distributed Systems: Customizable Load Balancer

## 1. Project Core Objective
The goal of this project is to implement a customizable, asynchronous load balancer that routes client HTTP requests across a dynamically scalable cluster of web server containers. To achieve an even distribution of traffic and prevent massive cache-miss reshuffles when servers scale up or down, the system utilizes a **Consistent Hashing Data Structure**. 

The system must maintain an active pool of $N=3$ default server instances. If a server instance crashes or fails, the load balancer must automatically detect the failure via health probes and spawn a new container to take its place.

---

## 2. Team Member Task Assignments & Instructions

### 👤 Task 1: Server Replicas & Containerization (Assigned to: Myra)
**Status: COMPLETED**
* **Objective:** Implement a lightweight web server and containerize it.
* **Requirements:**
  * Must listen strictly on internal port `5000`.
  * Provide a `GET /home` endpoint that returns a JSON success payload identifying its dynamic `SERVER_ID` env variable (e.g., `{"message": "Hello from Server: 123", "status": "successful"}`).
  * Provide a `GET /heartbeat` endpoint that emits an empty HTTP 200 payload for health checking.
  * Write a clean `Dockerfile` using a lightweight runtime (like Python slim).

---

### 👤 Task 2: Consistent Hash Map Data Structure (Assigned to: [Teammate Name])
**Status: IN PROGRESS**
* **Objective:** Build the circular data structure backend that maps requests to server slots.
* **Technical Constraints & Formulas:**
  * Total Slots in circular map ($M$): `512`.
  * Number of initial server containers ($N$): `3`.
  * Virtual Server replicas per container ($K$): `log(512) = 9`.
  * Request Mapping Hash Function: $H(i) = i + 2i + 17$.
  * Virtual Server Mapping Hash Function: $\Phi(i, j) = i + j + 2j + 25$.
* **Instructions:**
  * Map requests to slots via $slot = H(R_{id}) \pmod M$.
  * Map virtual servers via $slot_n = \Phi(i, j) \pmod M$.
  * Handle slot conflicts using **Linear Probing** or **Quadratic Probing** to find the next open slot.
  * Ensure requests map to the nearest available server slot traveling in a **clockwise direction**.

---

### 👤 Task 3: Load Balancer Orchestration & API (Assigned to: [Teammate Name])
**Status: IN PROGRESS**
* **Objective:** Create the main entryway container that handles client routing and configuration updates.
* **Instructions & API Endpoints to Implement:**
  * **Network Isolation:** Run everything inside a custom Docker network named `net1`. The load balancer must be exposed to the host machine on port `5000:5000`.
  * **`GET /rep`**: Return a JSON list of all currently active server replica hostnames.
  * **`POST /add`**: Accept a payload containing a count `n` and preferred `hostnames`. Spawn new container instances using the Task 1 image. If hostnames are omitted, generate them randomly. Throw a `400 Bad Request` if the hostname list length exceeds `n`.
  * **`DELETE /rm`**: Remove `n` server containers from the cluster. Prioritize removing preferred hostnames provided in the request payload; if unspecified, select containers randomly for deletion. Throw a `400 Bad Request` if the hostname list length exceeds `n`.
  * **`GET /<path>`**: Route inbound user requests to the server container chosen by the Task 2 Consistent Hashing module.
  * **Fault Tolerance Loop:** Continuously query `GET /heartbeat` on all active backend nodes. If a container times out or drops, immediately spawn a replacement instance with a randomly generated hostname to maintain system stability.

---

### 👤 Task 4: Testing & Performance Analysis (Collaborative / Assigned to: [Teammate Name])
**Status: UPCOMING**
* **Objective:** Run benchmarks and generate visual performance charts to document inside this README.
* **Experiments to Complete:**
  1. **A-1**: Fire 10,000 asynchronous requests at $N=3$ servers. Plot a bar chart showing request distributions per server to verify if load balancing is mathematically even.
  2. **A-2**: Scale $N$ sequentially from 2 up to 6 servers, firing 10,000 requests per tier. Plot a line chart tracking the average load to evaluate system scalability.
  3. **A-3**: Terminate a server container manually and demonstrate how quickly the load balancer detects the crash and spawns a healthy replacement.
  4. **A-4**: Modify the core hash functions $H(i)$ and $\Phi(i,j)$ and re-run experiments A-1 and A-2 to report the differences in balancing performance.

---

## 3. Git Workflow Rules for the Team
To ensure no one accidentally overwrites another member's code, we use dedicated feature branches:

1. **Never commit directly to `main`**.
2. Create your own workspace branch before coding:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/task[X]-[name]
