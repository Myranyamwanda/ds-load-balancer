from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class VirtualServer:
    server_id: int
    hostname: str
    replica_id: int


class ConsistentHash:
    """
    Consistent hashing ring.

    Requirements:
    - M = 512 slots
    - K = 9 virtual replicas
    - H(i)=i+2i+17
    - Phi(i,j)=i+j+2j+25
    - Linear probing
    - Clockwise lookup
    """

    def __init__(
        self,
        slots: int = 512,
        replicas: int = 9
    ):

        self.M = slots
        self.K = replicas

        self.ring: Dict[int, VirtualServer] = {}

        self.server_slots: Dict[str, List[int]] = {}

        self.server_ids: Dict[str, int] = {}

        # auto-increment IDs
        self.next_server_id = 1


    def request_hash(
        self,
        request_id: int
    ) -> int:

        return (
            request_id
            + (2 * request_id)
            + 17
        ) % self.M


    def virtual_server_hash(
        self,
        server_id: int,
        replica_id: int
    ) -> int:

        return (

            server_id
            + replica_id
            + (2 * replica_id)
            + 25

        ) % self.M


    def _find_empty_slot(
        self,
        initial_slot: int
    ) -> int:

        for offset in range(self.M):

            candidate=(

                initial_slot
                + offset

            ) % self.M


            if candidate not in self.ring:

                return candidate


        raise RuntimeError(
            "Hash ring full"
        )


    def add_server(
        self,
        hostname: str
    ) -> List[int]:

        """
        Add server using hostname only
        """

        if hostname in self.server_slots:

            raise ValueError(
                f"{hostname} already exists"
            )


        server_id=self.next_server_id

        self.next_server_id +=1


        occupied=[]


        for replica_id in range(
            self.K
        ):

            initial_slot=(
                self.virtual_server_hash(
                    server_id,
                    replica_id
                )
            )

            actual_slot=(
                self._find_empty_slot(
                    initial_slot
                )
            )

            self.ring[
                actual_slot
            ]=VirtualServer(

                server_id=server_id,

                hostname=hostname,

                replica_id=replica_id
            )

            occupied.append(
                actual_slot
            )


        self.server_slots[
            hostname
        ]=occupied

        self.server_ids[
            hostname
        ]=server_id


        return occupied


    def remove_server(
        self,
        hostname:str
    ) -> bool:

        if hostname not in self.server_slots:

            return False


        for slot in self.server_slots[
            hostname
        ]:

            self.ring.pop(
                slot,
                None
            )


        del self.server_slots[
            hostname
        ]

        del self.server_ids[
            hostname
        ]


        return True


    def get_server(
        self,
        request_id:int
    )->Optional[str]:


        if not self.ring:

            return None


        request_slot=(
            self.request_hash(
                request_id
            )
        )


        for offset in range(
            self.M
        ):

            candidate=(

                request_slot
                + offset

            )%self.M


            if candidate in self.ring:

                return self.ring[
                    candidate
                ].hostname


        return None


    def get_servers(
        self
    )->List[str]:

        return list(
            self.server_slots.keys()
        )


    def get_ring(self):

        return {

            slot:{

                "server_id":
                server.server_id,

                "hostname":
                server.hostname,

                "replica_id":
                server.replica_id

            }

            for slot,server
            in sorted(
                self.ring.items()
            )
        }


    def __len__(self):

        return len(
            self.server_slots
        )