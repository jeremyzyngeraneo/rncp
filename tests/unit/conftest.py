import requests
import grpc
import os
import pytest
from armonik.client import (
    ArmoniKResults,
    ArmoniKSubmitter,
    ArmoniKTasks,
    ArmoniKSessions,
)
from typing import List


grpc_endpoint = "localhost:5001"
calls_endpoint = "http://localhost:5000/calls.json"
reset_endpoint = "http://localhost:5000/reset"
data_folder = os.getcwd()


@pytest.fixture(scope="session", autouse=True)
def clean_up(request):
    """
    This fixture runs at the session scope and is automatically used before and after
    running all the tests. It set up and teardown the testing environments by:
        - creating dummy files before testing begins;
        - clear files after testing;
        - resets the mocking gRPC server counters to maintain a clean testing environment.

    Yields:
        None: This fixture is used as a context manager, and the test code runs between
        the 'yield' statement and the cleanup code.

    Raises:
        requests.exceptions.HTTPError: If an error occurs when attempting to reset
        the mocking gRPC server counters.
    """
    # Write dumm payload and data dependency to files for testing purposes
    with open(os.path.join(data_folder, "payload-id"), "wb") as f:
        f.write("payload".encode())
    with open(os.path.join(data_folder, "dd-id"), "wb") as f:
        f.write("dd".encode())

    # Run all the tests
    yield

    # Remove the temporary files created for testing
    os.remove(os.path.join(data_folder, "payload-id"))
    os.remove(os.path.join(data_folder, "dd-id"))

    # Reset the mock server counters
    try:
        response = requests.post(reset_endpoint)
        response.raise_for_status()
        print("\nMock server resetted.")
    except requests.exceptions.HTTPError as e:
        print("An error occurred when resetting the server: " + str(e))


def get_client(
    client_name: str, endpoint: str = grpc_endpoint
) -> [ArmoniKResults, ArmoniKSubmitter, ArmoniKTasks, ArmoniKSessions]:
    """
    Get the ArmoniK client instance based on the specified service name.

    Args:
        client_name (str): The name of the ArmoniK client to retrieve.
        endpoint (str, optional): The gRPC server endpoint. Defaults to grpc_endpoint.

    Returns:
        Union[ArmoniKResults, ArmoniKSubmitter, ArmoniKTasks, ArmoniKSessions, ARmoniKPartitions, AgentStub]:
            An instance of the specified ArmoniK client.

    Raises:
        ValueError: If the specified service name is not recognized.

    Example:
        >>> result_service = get_service("Results")
        >>> submitter_service = get_service("Submitter", "custom_endpoint")
    """
    channel = grpc.insecure_channel(endpoint).__enter__()
    match client_name:
        case "Results":
            return ArmoniKResults(channel)
        case "Submitter":
            return ArmoniKSubmitter(channel)
        case "Tasks":
            return ArmoniKTasks(channel)
        case "Sessions":
            return ArmoniKSessions(channel)
        case _:
            raise ValueError("Unknown service name: " + str(service_name))


def rpc_called(
    service_name: str, rpc_name: str, n_calls: int = 1, endpoint: str = calls_endpoint
) -> bool:
    """Check if a remote procedure call (RPC) has been made a specified number of times.
    This function uses ArmoniK.Api.Mock. It just gets the '/calls.json' endpoint.

    Args:
        service_name (str): The name of the service providing the RPC.
        rpc_name (str): The name of the specific RPC to check for the number of calls.
        n_calls (int, optional): The expected number of times the RPC should have been called. Default is 1.
        endpoint (str, optional): The URL of the remote service providing RPC information. Default to
            calls_endpoint.

    Returns:
        bool: True if the specified RPC has been called the expected number of times, False otherwise.

    Raises:
        requests.exceptions.RequestException: If an error occurs when requesting ArmoniK.Api.Mock.

    Example:
    >>> rpc_called('http://localhost:5000/calls.json', 'Versions', 'ListVersionss', 0)
    True
    """
    response = requests.get(endpoint)
    response.raise_for_status()
    data = response.json()

    # Check if the RPC has been called n_calls times
    if data[service_name][rpc_name] == n_calls:
        return True
    return False


def all_rpc_called(
    service_name: str, missings: List[str] = [], endpoint: str = calls_endpoint
) -> bool:
    """
    Check if all remote procedure calls (RPCs) in a service have been made at least once.
    This function uses ArmoniK.Api.Mock. It just gets the '/calls.json' endpoint.

    Args:
        service_name (str): The name of the service containing the RPC information in the response.
        endpoint (str, optional): The URL of the remote service providing RPC information. Default is
            the value of calls_endpoint.
        missings (List[str], optional): A list of RPCs known to be not implemented. Default is an empty list.

    Returns:
        bool: True if all RPCs in the specified service have been called at least once, False otherwise.

    Raises:
        requests.exceptions.RequestException: If an error occurs when requesting ArmoniK.Api.Mock.

    Example:
    >>> all_rpc_called('http://localhost:5000/calls.json', 'Versions')
    False
    """
    response = requests.get(endpoint)
    response.raise_for_status()
    data = response.json()

    missing_rpcs = []

    # Check if all RPCs in the service have been called at least once
    for rpc_name, rpc_num_calls in data[service_name].items():
        if rpc_num_calls == 0:
            missing_rpcs.append(rpc_name)
    if missing_rpcs:
        if missings == missing_rpcs:
            return True
        print(f"RPCs not implemented in {service_name} service: {missing_rpcs}.")
        return False
    return True
