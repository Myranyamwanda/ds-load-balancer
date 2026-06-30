import asyncio
import httpx


async def monitor(
    replica_manager,
    hash_ring
):

    while True:

        dead = []

        for hostname in list(
            replica_manager.active_servers.keys()
        ):

            try:

                # Get the mapped host port
                port = replica_manager.get_port(
                    hostname
                )

                print(
                    f"Checking {hostname} on localhost:{port}"
                )

                async with httpx.AsyncClient() as client:

                    response = await client.get(
                        f"http://localhost:{port}/heartbeat",
                        timeout=2
                    )

                print(
                    f"{hostname}: {response.status_code}"
                )

                if response.status_code != 200:

                    dead.append(
                        hostname
                    )


            except Exception as e:

                print(
                    f"ERROR on {hostname}: {type(e).__name__}: {e}"
                )

                dead.append(
                    hostname
                )


        for server in dead:

            print(
                f"Replacing {server}"
            )

            try:

                replica_manager.remove(
                    server
                )

                hash_ring.remove_server(
                    server
                )

            except Exception as e:

                print(
                    f"Cleanup failed: {e}"
                )


            replacement = (
                replica_manager.generate_hostname()
            )

            print(
                f"Starting replacement: {replacement}"
            )

            replica_manager.spawn(
                replacement
            )

            hash_ring.add_server(
                replacement
            )


        await asyncio.sleep(5)