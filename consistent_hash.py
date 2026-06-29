from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class VirtualServer:
    server_id: int
    hostname: str
    replica_id: int


class ConsistentHashMap:
    """
    Consistent hashing ring.

    Requirements:
    - M = 512 slots
    - K = 9 virtual replicas per physical server
    - H(i) = i + 2i + 17
    - Phi(i, j) = i + j + 2j + 25
    - Linear probing for collisions
    - Clockwise request lookup
    """

    def __init__(self, slots: int = 512, replicas: int = 9) -> None:
        if slots <= 0:
            raise ValueError("slots must be greater than zero")

        if replicas <= 0:
            raise ValueError("replicas must be greater than zero")

        self.M = slots
        self.K = replicas

        self.ring: Dict[int, VirtualServer] = {}
        self.server_slots: Dict[str, List[int]] = {}
        self.server_ids: Dict[str, int] = {}

    def request_hash(self, request_id: int) -> int:
        """
        Request mapping function:

        H(i) = i + 2i + 17
        """
        return (request_id + (2 * request_id) + 17) % self.M

    def virtual_server_hash(
        self,
        server_id: int,
        replica_id: int
    ) -> int:
        """
        Virtual server mapping function:

        Phi(i, j) = i + j + 2j + 25
        """
        return (
            server_id
            + replica_id
            + (2 * replica_id)
            + 25
        ) % self.M

    def _find_empty_slot(self, initial_slot: int) -> int:
        """
        Find the next available slot using linear probing.
        """
        for offset in range(self.M):
            candidate = (initial_slot + offset) % self.M

            if candidate not in self.ring:
                return candidate

        raise RuntimeError("The hash ring is full")

    def add_server(
        self,
        server_id: int,
        hostname: str
    ) -> List[int]:
        """
        Add a physical server and its K virtual replicas.
        """
        if not isinstance(server_id, int):
            raise TypeError("server_id must be an integer")

        if not isinstance(hostname, str) or not hostname.strip():
            raise ValueError("hostname must be a non-empty string")

        hostname = hostname.strip()

        if hostname in self.server_slots:
            raise ValueError(
                f"Server '{hostname}' already exists"
            )

        if server_id in self.server_ids.values():
            raise ValueError(
                f"Server ID '{server_id}' already exists"
            )

        if len(self.ring) + self.K > self.M:
            raise RuntimeError(
                "Not enough free slots for another server"
            )

        occupied_slots: List[int] = []

        for replica_id in range(self.K):
            initial_slot = self.virtual_server_hash(
                server_id,
                replica_id
            )

            actual_slot = self._find_empty_slot(initial_slot)

            self.ring[actual_slot] = VirtualServer(
                server_id=server_id,
                hostname=hostname,
                replica_id=replica_id
            )

            occupied_slots.append(actual_slot)

        self.server_slots[hostname] = occupied_slots
        self.server_ids[hostname] = server_id

        return occupied_slots.copy()

    def remove_server(self, hostname: str) -> bool:
        """
        Remove a physical server and all its virtual replicas.
        """
        if hostname not in self.server_slots:
            return False

        for slot in self.server_slots[hostname]:
            self.ring.pop(slot, None)

        del self.server_slots[hostname]
        self.server_ids.pop(hostname, None)

        return True

    def get_server(self, request_id: int) -> Optional[str]:
        """
        Map a request to the nearest occupied slot clockwise.
        """
        details = self.get_server_details(request_id)

        if details is None:
            return None

        return details["hostname"]

    def get_server_details(
        self,
        request_id: int
    ) -> Optional[dict]:
        """
        Return detailed request mapping information.
        """
        if not self.ring:
            return None

        request_slot = self.request_hash(request_id)

        for offset in range(self.M):
            candidate = (request_slot + offset) % self.M

            if candidate in self.ring:
                virtual_server = self.ring[candidate]

                return {
                    "request_id": request_id,
                    "request_slot": request_slot,
                    "selected_slot": candidate,
                    "server_id": virtual_server.server_id,
                    "hostname": virtual_server.hostname,
                    "replica_id": virtual_server.replica_id
                }

        return None

    def get_servers(self) -> List[str]:
        """
        Return all active physical server hostnames.
        """
        return list(self.server_slots.keys())

    def get_server_slots(self, hostname: str) -> List[int]:
        """
        Return the virtual slots occupied by one server.
        """
        return self.server_slots.get(hostname, []).copy()

    def get_ring(self) -> Dict[int, dict]:
        """
        Return the occupied ring slots in serializable form.
        """
        return {
            slot: {
                "server_id": virtual_server.server_id,
                "hostname": virtual_server.hostname,
                "replica_id": virtual_server.replica_id
            }
            for slot, virtual_server in sorted(self.ring.items())
        }

    def __len__(self) -> int:
        """
        Return the number of physical servers.
        """
        return len(self.server_slots)