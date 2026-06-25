
## 1. Project Core Objective
[cite_start]The goal of this project is to implement a customizable, asynchronous load balancer that routes client HTTP requests across a dynamically scalable cluster of web server containers[cite: 33, 79]. [cite_start]To achieve an even distribution of traffic and prevent massive cache-miss reshuffles when servers scale up or down, the system utilizes a **Consistent Hashing Data Structure**[cite: 33, 36, 185]. 

[cite_start]The system must maintain an active pool of $N=3$ default server instances[cite: 38, 69]. [cite_start]If a server instance crashes or fails, the load balancer must automatically detect the failure via health probes and spawn a new container to take its place[cite: 39, 81].

---

## 2. Team Member Task Assignments & Instructions

### 👤 Task 1: Server Replicas & Containerization (Assigned to: Myra)
**Status: COMPLETED**
* [cite_start]**Objective:** Implement a lightweight web server and containerize it[cite: 51, 64].
* **Requirements:**
  * [cite_start]Must listen strictly on internal port `5000`[cite: 51].
  * [cite_start]Provide a `GET /home` endpoint that returns a JSON success payload identifying its dynamic `SERVER_ID` env variable (e.g., `{"message": "Hello from Server: 123", "status": "successful"}`)[cite: 52, 54, 55].
  * [cite_start]Provide a `GET /heartbeat` endpoint that emits an empty HTTP 200 payload for health checking[cite: 60, 62, 63].
  * [cite_start]Write a clean `Dockerfile` using a lightweight runtime (like Python slim)[cite: 64].

---

### 👤 Task 2: Consistent Hash Map Data Structure (Assigned to: [Teammate Name])
**Status: IN PROGRESS**
* [cite_start]**Objective:** Build the circular data structure backend that maps requests to server slots[cite: 67, 198].
* **Technical Constraints & Formulas:**
  * [cite_start]Total Slots in circular map ($M$): `512`[cite: 69].
  * [cite_start]Number of initial server containers ($N$): `3`[cite: 69].
  * [cite_start]Virtual Server replicas per container ($K$): `log(512) = 9`[cite: 69].
  * [cite_start]Request Mapping Hash Function: $H(i) = i + 2i + 17$[cite: 69].
  * [cite_start]Virtual Server Mapping Hash Function: $\Phi(i, j) = i + j + 2j + 25$[cite: 70].
* **Instructions:**
  * [cite_start]Map requests to slots via $slot = H(R_{id}) \pmod M$[cite: 199].
  * [cite_start]Map virtual servers via $slot_n = \Phi(i, j) \pmod M$[cite: 222].
  * [cite_start]Handle slot conflicts using **Linear Probing** or **Quadratic Probing** to find the next open slot[cite: 72].
  * [cite_start]Ensure requests map to the nearest available server slot traveling in a **clockwise direction**[cite: 202].

---

### 👤 Task 3: Load Balancer Orchestration & API (Assigned to: [Teammate Name])
**Status: IN PROGRESS**
* [cite_start]**Objective:** Create the main entryway container that handles client routing and configuration updates[cite: 79].
* **Instructions & API Endpoints to Implement:**
  * [cite_start]**Network Isolation:** Run everything inside a custom Docker network named `net1`[cite: 4, 37]. [cite_start]The load balancer must be exposed to the host machine on port `5000:5000`[cite: 17, 82].
  * [cite_start]**`GET /rep`**: Return a JSON list of all currently active server replica hostnames[cite: 83, 84].
  * [cite_start]**`POST /add`**: Accept a payload containing a count `n` and preferred `hostnames`[cite: 93]. [cite_start]Spawn new container instances using the Task 1 image[cite: 79, 92]. [cite_start]If hostnames are omitted, generate them randomly[cite: 109]. [cite_start]Throw a `400 Bad Request` if the hostname list length exceeds `n`[cite: 110].
  * [cite_start]**`DELETE /rm`**: Remove `n` server containers from the cluster[cite: 119, 120]. [cite_start]Prioritize removing preferred hostnames provided in the request payload [cite: 120][cite_start]; if unspecified, select containers randomly for deletion[cite: 136]. [cite_start]Throw a `400 Bad Request` if the hostname list length exceeds `n`[cite: 137].
  * [cite_start]**`GET /<path>`**: Route inbound user requests to the server container chosen by the Task 2 Consistent Hashing module[cite: 144].
  * [cite_start]**Fault Tolerance Loop:** Continuously query `GET /heartbeat` on all active backend nodes[cite: 60, 61]. [cite_start]If a container times out or drops, immediately spawn a replacement instance with a randomly generated hostname to maintain system stability[cite: 39, 81].

---

### 👤 Task 4: Testing & Performance Analysis (Collaborative / Assigned to: [Teammate Name])
**Status: UPCOMING**
* [cite_start]**Objective:** Run benchmarks and generate visual performance charts to document inside this README[cite: 43, 157].
* **Experiments to Complete:**
  1. **A-1**: Fire 10,000 asynchronous requests at $N=3$ servers. [cite_start]Plot a bar chart showing request distributions per server to verify if load balancing is mathematically even[cite: 158, 159].
  2. **A-2**: Scale $N$ sequentially from 2 up to 6 servers, firing 10,000 requests per tier. [cite_start]Plot a line chart tracking the average load to evaluate system scalability[cite: 160, 161, 162].
  3. [cite_start]**A-3**: Terminate a server container manually and demonstrate how quickly the load balancer detects the crash and spawns a healthy replacement[cite: 163].
  4. [cite_start]**A-4**: Modify the core hash functions $H(i)$ and $\Phi(i,j)$ and re-run experiments A-1 and A-2 to report the differences in balancing performance[cite: 164].

---

## 3. Git Workflow Rules for the Team
To ensure no one accidentally overwrites another member's code, we use dedicated feature branches:

1. **Never commit directly to `main`**.
2. Create your own workspace branch before coding:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/task[X]-[name]
