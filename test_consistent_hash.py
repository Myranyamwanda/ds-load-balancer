from collections import Counter

from consistent_hash import ConsistentHashMap


# Test whether the two hash formulas return the expected slots
def test_hash_formulas() -> None:
    hash_map = ConsistentHashMap()

    assert hash_map.request_hash(10) == 47
    assert hash_map.virtual_server_hash(2, 3) == 36

    print("Hash formula tests passed")


# Test what happens when there are no servers in the ring
def test_empty_ring() -> None:
    empty_hash_map = ConsistentHashMap()

    assert empty_hash_map.get_server(1) is None
    assert empty_hash_map.get_server_details(1) is None

    print("\nEmpty ring test passed")


# Test that duplicate hostnames are not allowed
def test_duplicate_server() -> None:
    hash_map = ConsistentHashMap()
    hash_map.add_server(1, "server1")

    try:
        hash_map.add_server(2, "server1")
    except ValueError:
        print("Duplicate hostname test passed")
    else:
        raise AssertionError(
            "Duplicate hostname should raise ValueError"
        )


# Add the three default servers to the hash ring
def test_add_servers(hash_map: ConsistentHashMap) -> None:
    print("\nAdding three default servers...")

    server1_slots = hash_map.add_server(1, "server1")
    server2_slots = hash_map.add_server(2, "server2")
    server3_slots = hash_map.add_server(3, "server3")

    print("Server 1 slots:", server1_slots)
    print("Server 2 slots:", server2_slots)
    print("Server 3 slots:", server3_slots)

    # Each physical server should have 9 virtual replicas
    assert len(server1_slots) == 9
    assert len(server2_slots) == 9
    assert len(server3_slots) == 9

    # The hash ring should contain 3 physical servers
    assert len(hash_map) == 3

    print("\nActive servers:")
    print(hash_map.get_servers())


# Display all occupied slots in the circular hash map
def display_ring(hash_map: ConsistentHashMap) -> None:
    print("\nOccupied slots:")

    for slot, information in hash_map.get_ring().items():
        print(slot, information)


# Show how sample requests are mapped to servers
def display_request_mappings(
    hash_map: ConsistentHashMap,
    start: int = 1,
    end: int = 20
) -> None:
    print("\nRequest mappings:")

    for request_id in range(start, end + 1):
        details = hash_map.get_server_details(request_id)

        if details is None:
            print(f"Request {request_id}: no server available")
            continue

        print(
            f"Request {request_id}: "
            f"request slot={details['request_slot']}, "
            f"selected slot={details['selected_slot']}, "
            f"server={details['hostname']}"
        )


# Send many requests and count how many go to each server
def test_distribution(
    hash_map: ConsistentHashMap,
    total_requests: int = 10000
) -> None:
    distribution = Counter()

    for request_id in range(1, total_requests + 1):
        selected_server = hash_map.get_server(request_id)

        if selected_server is not None:
            distribution[selected_server] += 1

    print(f"\nDistribution for {total_requests} requests:")

    for server in hash_map.get_servers():
        count = distribution[server]
        percentage = (count / total_requests) * 100

        print(
            f"{server}: "
            f"{count} requests "
            f"({percentage:.2f}%)"
        )


# Remove one server and confirm its virtual replicas are removed
def test_remove_server(hash_map: ConsistentHashMap) -> None:
    print("\nRemoving server2...")

    removed = hash_map.remove_server("server2")

    assert removed is True
    assert "server2" not in hash_map.get_servers()
    assert len(hash_map) == 2

    print("Remaining servers:", hash_map.get_servers())

    # Display request mappings after server2 has been removed
    print("\nMappings after removal:")

    for request_id in range(1, 11):
        selected_server = hash_map.get_server(request_id)

        print(
            f"Request {request_id} -> "
            f"{selected_server}"
        )


# Run all tests in the correct order
def main() -> None:
    test_hash_formulas()
    test_empty_ring()
    test_duplicate_server()

    # Create the main hash ring using the assignment values
    hash_map = ConsistentHashMap(
        slots=512,
        replicas=9
    )

    test_add_servers(hash_map)
    display_ring(hash_map)
    display_request_mappings(hash_map)
    test_distribution(hash_map)
    test_remove_server(hash_map)

    print("\nAll tests completed successfully")


# Start the program only when this file is run directly
if __name__ == "__main__":
    main()