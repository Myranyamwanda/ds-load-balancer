import docker
import uuid

client = docker.from_env()

IMAGE_NAME = "web-server"
NETWORK_NAME = "net1"


class ReplicaManager:

    def __init__(self):

        self.active_servers={}


    def generate_hostname(self):

        return f"srv-{uuid.uuid4().hex[:6]}"


    def spawn(self, hostname):

        container = client.containers.run(
            IMAGE_NAME,
            detach=True,
            network=NETWORK_NAME,
            hostname=hostname,
            name=hostname,
            environment={
                "SERVER_ID": hostname
            },
            ports={
                "5000/tcp": None
            }
        )

        self.active_servers[hostname] = container

        return hostname


    def remove(self,hostname):

        container=self.active_servers[
            hostname
        ]

        container.stop()
        container.remove()

        del self.active_servers[
            hostname
        ]


    def get_ip(self,hostname):

        container=self.active_servers[
            hostname
        ]

        container.reload()

        return container.attrs[
            "NetworkSettings"
        ][
            "Networks"
        ][
            NETWORK_NAME
        ][
            "IPAddress"
        ]
    
    def get_port(self, hostname):

        container = self.active_servers[hostname]

        container.reload()

        return container.attrs[
            "NetworkSettings"
        ][
            "Ports"
        ][
            "5000/tcp"
        ][0][
            "HostPort"
        ]