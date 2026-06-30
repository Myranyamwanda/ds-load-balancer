import asyncio
import re
import subprocess
import time

import httpx
import matplotlib.pyplot as plt
import requests

# The load balancer's address on your laptop
BASE_URL = "http://localhost:5050"


# -------------------------------------------------------
# Helper: send one request to /home and return the server
# name from the response, e.g. "server0" or "srv-abc123"
# -------------------------------------------------------

async def fetch_one(client, semaphore):
    async with semaphore:
        try:
            r = await client.get(BASE_URL + "/home", timeout=10)
            # Response looks like: {"message": "Hello from Server: server0", ...}
            # We extract just the server name using a regex
            match = re.search(r"Hello from Server:\s*([\w-]+)", r.text)
            if match:
                return match.group(1)
        except Exception:
            pass
    return None


# Helper: send N requests concurrently, return a dict
# mapping each server name to how many requests it got


async def run_requests(total):
    # Semaphore limits how many requests run at the same time.
    # 100 at once is enough to be fast without overwhelming the server.
    semaphore = asyncio.Semaphore(100)
    async with httpx.AsyncClient() as client:
        tasks = [fetch_one(client, semaphore) for _ in range(total)]
        responses = await asyncio.gather(*tasks)

    # Count how many times each server name appeared
    counts = {}
    for name in responses:
        if name is not None:
            counts[name] = counts.get(name, 0) + 1
    return counts


# -------------------------------------------------------
# Helper: ask the load balancer which servers are running
# -------------------------------------------------------

def get_replicas():
    r = requests.get(BASE_URL + "/rep")
    return r.json()["replicas"]


# Helper: add or remove servers to reach the target number


def set_server_count(target):
    current = get_replicas()
    diff = target - len(current)

    if diff > 0:
        # Add more servers (let the load balancer pick names)
        requests.post(BASE_URL + "/add", json={"n": diff, "hostnames": []})
    elif diff < 0:
        # Remove some servers (let the load balancer pick which ones)
        requests.delete(BASE_URL + "/rm", json={"n": abs(diff), "hostnames": []})

    # Wait a moment for new containers to finish starting up
    time.sleep(3)
    print(f"  Servers now running: {get_replicas()}")


# A-1: Send 10,000 requests to N=3 servers and plot a
#       bar chart showing how the load was distributed


def experiment_a1():
    print("\n-- A-1: Load distribution with N=3 servers ---")

    print("Setting server count to 3...")
    set_server_count(3)

    print("Sending 10,000 requests...")
    counts = asyncio.run(run_requests(10000))

    # Print results
    print("\nResults:")
    total = sum(counts.values())
    for server, count in sorted(counts.items()):
        print(f"  {server}: {count} requests ({count / total * 100:.1f}%)")

    # Draw bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(counts.keys(), counts.values(), color="steelblue")
    plt.axhline(y=10000 / 3, color="red", linestyle="--", label="Ideal (3333)")
    plt.xlabel("Server")
    plt.ylabel("Requests handled")
    plt.title("A-1: Request distribution across 3 servers (10,000 requests)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("a1_bar_chart.png")
    print("\nChart saved as a1_bar_chart.png")


# A-2: Increase N from 2 to 6 servers, send 10,000
#       requests each time, and plot the average load


def experiment_a2():
    print("\n--- A-2: Scalability test (N = 2 to 6 servers) ---")

    server_counts = [2, 3, 4, 5, 6]
    averages = []

    for n in server_counts:
        print(f"\nSetting server count to {n}...")
        set_server_count(n)

        print(f"Sending 10,000 requests...")
        counts = asyncio.run(run_requests(10000))

        avg = sum(counts.values()) / n
        averages.append(avg)
        print(f"  Average load per server: {avg:.1f} requests")

    # Draw line chart
    plt.figure(figsize=(8, 5))
    plt.plot(server_counts, averages, marker="o", color="steelblue")
    plt.xlabel("Number of servers (N)")
    plt.ylabel("Average requests per server")
    plt.title("A-2: Average load per server as N increases")
    plt.tight_layout()
    plt.savefig("a2_line_chart.png")
    print("\nChart saved as a2_line_chart.png")



# A-3: Kill one server and measure how long the load
#       balancer takes to detect the crash and replace it


def experiment_a3():
    print("\n--- A-3: Failure detection and recovery ---")

    replicas = get_replicas()
    target_count = len(replicas)
    victim = replicas[0]

    print(f"Current servers: {replicas}")
    print(f"Killing '{victim}' now...")

    start = time.time()
    subprocess.run(["docker", "kill", victim])

    print("Polling /rep every second to detect recovery...")
    while True:
        time.sleep(1)
        current = get_replicas()
        elapsed = round(time.time() - start, 1)
        print(f"  t={elapsed}s -> {current}")

        # Recovery is complete when the dead server is gone
        # and the count is back to what it was before
        if victim not in current and len(current) == target_count:
            print(f"\nRecovered in {elapsed} seconds.")
            break

        if elapsed > 60:
            print("\nTimed out. Check: docker logs load-balancer")
            break

# Main menu

if __name__ == "__main__":
    print("Task 4 - Load Balancer Analysis")
    print("Which experiment do you want to run?")
    print("  1 = A-1 (bar chart, N=3, 10,000 requests)")
    print("  2 = A-2 (line chart, N=2 to 6)")
    print("  3 = A-3 (kill a server, watch it recover)")

    choice = input("\nEnter 1, 2, or 3: ").strip()

    if choice == "1":
        experiment_a1()
    elif choice == "2":
        experiment_a2()
    elif choice == "3":
        experiment_a3()
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")