import sys
import argparse
from argparse import RawTextHelpFormatter
import grpc
import armonik_cli
import armonik_cli.session as session
import armonik_cli.task as task
import armonik_cli.result as result
from armonik.client.sessions import ArmoniKSessions, SessionFieldFilter
from armonik.client.tasks import ArmoniKTasks
from armonik.client.results import ArmoniKResults, ResultFieldFilter
from armonik.common.enumwrapper import (
    SESSION_STATUS_RUNNING,
    SESSION_STATUS_CANCELLED,
    RESULT_STATUS_COMPLETED,
    RESULT_STATUS_CREATED,
)


def create_channel(endpoint: str, ca: str, key: str, cert: str) -> grpc.Channel:
    """
    Create a gRPC channel for communication with the ArmoniK control plane

    Args:
        ca (str): CA file path for mutual TLS
        cert (str): Certificate file path for mutual TLS
        key (str): Private key file path for mutual TLS
        endpoint (str): ArmoniK control plane endpoint

    Returns:
        grpc.Channel: gRPC channel for communication
    """
    try:
        if ca:
            with open(ca, "rb") as ca_file:
                ca_data = ca_file.read()
            if cert and key:
                with open(cert, "rb") as cert_file, open(key, "rb") as key_file:
                    key_data = key_file.read()
                    cert_data = cert_file.read()
            else:
                key_data = None
                cert_data = None

            credentials = grpc.ssl_channel_credentials(ca_data, key_data, cert_data)
            return grpc.secure_channel(endpoint, credentials)
        else:
            return grpc.insecure_channel(endpoint)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="ArmoniK Admin CLI to perform administration tasks for ArmoniK",
        prog="akctl",
        epilog="EXAMPLES\n  akctl session -h\n\nLEARN MORE\n  Use 'akctl <command> <subcommand> --help' for more information",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=armonik_cli.__version__
    )
    parser.add_argument(
        "--endpoint",
        default="localhost:5001",
        help="ArmoniK control plane endpoint"
    )
    parser.add_argument(
        "--ca",
        help="CA file for mutual TLS"
    )
    parser.add_argument(
        "--cert",
        help="Certificate for mutual TLS"
    )
    parser.add_argument(
        "--key",
        help="Private key for mutual TLS"
    )
    parser.set_defaults(func=lambda _: parser.print_help())

    # TOP LEVEL COMMANDS
    subparsers = parser.add_subparsers(title="COMMANDS")

    session_parser = subparsers.add_parser("session", help="manage sessions")
    session_parser.set_defaults(func=lambda _: session_parser.print_help())

    task_parser = subparsers.add_parser("task", help="manage tasks")
    task_parser.set_defaults(func=lambda _: task_parser.print_help())

    result_parser = subparsers.add_parser("result", help="manage results")
    result_parser.set_defaults(func=lambda _: result_parser.print_help())

    partition_parser = subparsers.add_parser("partition", help="manage partitions")
    partition_parser.set_defaults(func=lambda _: partition_parser.print_help())

    config_parser = subparsers.add_parser(
        "config",
        help="modify akconfig file (control plane URL, certificate for SSL, etc)"
    )
    config_parser.set_defaults(func=lambda _: config_parser.print_help())

    ### SESSION SUBCOMMAND ###
    session_subparsers = session_parser.add_subparsers(title="SESSION SUBCOMMANDS")

    # LIST SESSION
    list_session_parser = session_subparsers.add_parser(
        "list", help="list sessions with specific filters"
    )
    list_session_parser.add_argument(
        "--running",
        dest="filter",
        default=None,
        action="store_const",
        const=SessionFieldFilter.STATUS == SESSION_STATUS_RUNNING,
        help="Select running sessions"
    )
    list_session_parser.add_argument(
        "--cancelled",
        dest="filter",
        default=None,
        action="store_const",
        const=SessionFieldFilter.STATUS == SESSION_STATUS_CANCELLED,
        help="Select cancelled sessions"
    )
    list_session_parser.set_defaults(
        func=lambda args: session.list_sessions(session_client, args.filter)
    )

    # GET SESSION
    get_session_parser = session_subparsers.add_parser(
        "get", help="get sessions with specific filters"
    )
    get_session_parser.add_argument(
        dest="session_ids", nargs="+", help="Select ID from session"
    )
    get_session_parser.set_defaults(
        func=lambda args: session.check_session(session_client, args.session_ids)
    )

    ### TASK SUBCOMMAND ###
    task_subparsers = task_parser.add_subparsers(title="TASK SUBCOMMANDS")

    # LIST TASKS
    list_task_parser = task_subparsers.add_parser(
        "list", help="List tasks with specific filters"
    )
    list_task_parser.add_argument(
        "--session-id",
        default=None,
        dest="session_id",
        help="Select ID from SESSION"
    )
    list_task_parser.add_argument(
        "--partition",
        default=None,
        dest="partition_name",
        help="Select name of Partition"
    )
    list_task_parser.set_defaults(
        func=lambda args: task.list_tasks(
            task_client,
            task.create_task_filter(
                args.partition_name, args.session_id, False
            ) if args.partition_name and args.session_id else
            task.create_task_filter(
                args.partition_name, args.session_id, False
            ) if args.session_id else
            task.create_task_filter(
                args.partition_name, args.session_id, False
            ) if args.partition_name else None,
        )
    )

    # CHECK TASK
    get_task_parser = task_subparsers.add_parser(
        "get", help="List tasks with specific filters"
    )
    get_task_parser.add_argument(
        dest="task_ids", nargs="+", help="Select ID from TASK"
    )
    get_task_parser.set_defaults(
        func=lambda args: task.check_task(task_client, args.task_ids)
    )

    # TASK DURATION
    task_duration_parser = task_subparsers.add_parser(
        "duration", help="Print task durations per partition"
    )
    task_duration_parser.add_argument(
        dest="session_id", help="Select ID from SESSION"
    )
    task_duration_parser.set_defaults(
        func=lambda args: task.get_task_durations(
            task_client, task.create_task_filter(False, args.session_id, False)
        )
    )

    ### RESULT SUBCOMMAND ###
    result_subparsers = result_parser.add_subparsers(title="RESULT SUBCOMMANDS")

    # LIST RESULT
    list_result_parser = result_subparsers.add_parser(
        "list", help="list results with specific filters"
    )
    list_result_parser.add_argument(
        "--completed",
        dest="filter",
        default=None,
        action="store_const",
        const=ResultFieldFilter.STATUS == RESULT_STATUS_COMPLETED,
        help="Select running sessions"
    )
    list_result_parser.add_argument(
        "--created",
        dest="filter",
        default=None,
        action="store_const",
        const=ResultFieldFilter.STATUS == RESULT_STATUS_CREATED,
        help="Select cancelled sessions"
    )
    list_result_parser.set_defaults(
        func=lambda args: result.list_results(result_client, args.filter)
    )


    args = parser.parse_args()
    grpc_channel = create_channel(args.endpoint, args.ca, args.key, args.cert)
    task_client = ArmoniKTasks(grpc_channel)
    session_client = ArmoniKSessions(grpc_channel)
    result_client = ArmoniKResults(grpc_channel)
    args.func(args)


if __name__ == "__main__":
    main()
