import sys
import argparse
from argparse import RawTextHelpFormatter
import grpc
from armonik.client.sessions import ArmoniKSessions, SessionFieldFilter
from armonik.client.tasks import ArmoniKTasks, TaskFieldFilter
from armonik.client.results import ArmoniKResults, ResultFieldFilter
from armonik.common.enumwrapper import TASK_STATUS_ERROR, TASK_STATUS_CREATING , SESSION_STATUS_RUNNING, SESSION_STATUS_CANCELLED, RESULT_STATUS_COMPLETED, RESULT_STATUS_CREATED
from armonik.common import Filter


def create_channel(endpoint: str,  ca: str, key: str, cert: str) -> grpc.Channel:
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
            with open(ca, 'rb') as ca_file:
                ca_data = ca_file.read()
            if cert and key:
                with open(cert, 'rb') as cert_file, open(key, 'rb') as key_file:
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



def list_sessions(client: ArmoniKSessions, session_filter: Filter):
    """
    List sessions with filter options

    Args:
        client (ArmoniKSessions): ArmoniKSessions instance for session management
        session_filter (Filter) : Filter for the session
    """
    page = 0
    sessions = client.list_sessions(session_filter, page=page)
    
    while len(sessions[1]) > 0:
        for session in sessions[1]:
            print(f'Session ID: {session.session_id}')
        page += 1
        sessions = client.list_sessions(session_filter, page=page)

    print(f'\nNumber of sessions: {sessions[0]}\n')


def check_session(client: ArmoniKSessions, session_ids: list):
    """
    Check and display information for ArmoniKSessions with given session IDs

    Args:
        client (ArmoniKSessions): ArmoniKSessions instance for session management
        session_ids (list): List of session IDs to check.
    """
    for session_id in session_ids:
        sessions = client.get_session(session_id)
        if session_id == sessions.session_id:
            print(f"\nTask information for task ID {session_id} :\n")
            print(sessions)
        else:
            print(f"No task found with ID {session_id}")


def cancel_sessions(client: ArmoniKSessions, sessions: list):
    """
    Cancel sessions with a list of session IDs or all sessions running

    Args:
        client (ArmoniKSessions): Instance of the class with cancel_session method
        sessions (list): List of session IDs to cancel
    """
    for session_id in sessions:
        try:
            client.cancel_session(session_id)
            print(f"Session {session_id} canceled successfully")
        except grpc._channel._InactiveRpcError as error:
            print(f"Error for canceling session {session_id}: {error.details()}")


def create_task_filter(partition:str, session_id: str, creating: bool) -> Filter:
    """
    Create a task Filter based on the provided options

    Args:
        session_id (str): Session ID to filter tasks
        all (bool): List all tasks regardless of status
        creating (bool): List only tasks in creating status
        error (bool): List only tasks in error status

    Returns:
        Filter object
    """
    if session_id:
        tasks_filter = TaskFieldFilter.SESSION_ID == session_id
    elif session_id and partition:
        tasks_filter = (TaskFieldFilter.SESSION_ID == session_id) & (TaskFieldFilter.PARTITION_ID == partition)
    elif partition:
        tasks_filter = TaskFieldFilter.PARTITION_ID == partition
    elif creating and creating:
        tasks_filter = (TaskFieldFilter.SESSION_ID == session_id) & (TaskFieldFilter.STATUS == TASK_STATUS_CREATING)
    else:
            raise ValueError("SELECT ARGUMENT [--creating ]")

    return tasks_filter
    
def list_tasks(client: ArmoniKTasks, task_filter: Filter):
    """
    List tasks associated with the specified sessions based on filter options

    Args:
        client (ArmoniKTasks): ArmoniKTasks instance for task management
        task_filter (Filter): Filter for the task
    """

    page = 0
    tasks = client.list_tasks(task_filter, page=page)
    while len(tasks[1]) > 0:
        for task in tasks[1]:
            print(f'Task ID: {task.id}')
        page += 1
        tasks = client.list_tasks(task_filter, page=page)

    print(f"\nTotal tasks: {tasks[0]}\n")

def calculate_tasks_duration(client: ArmoniKTasks, task_filter: Filter) -> float:
    """
    Calculate the total duration of tasks.

    Args:
        client (ArmoniKTasks): ArmoniKTasks instance for task management
        task_filter (Filter): Filter for the task

    Returns:
        float: Total duration of tasks in seconds
    """
    total_duration = 0.0
    page = 0
    tasks = client.list_tasks(task_filter, page=page)
    while len(tasks[1]) > 0:
        for task in tasks[1]:
            if task.started_at and task.ended_at:
                duration = (task.ended_at - task.started_at).total_seconds()
                # on soustrait la date du debut de la tache a la date de fin et on converti en seconde
                print(f"{task.id} duration in seconds: {duration}")
                total_duration += duration
        page += 1
        tasks = client.list_tasks(task_filter, page=page)
    print(f"\nTotal duration of tasks in seconds: {total_duration}\n")



def check_task(client: ArmoniKTasks, task_ids: list):
    """
    Check the status of a task based on its ID.

    Args:
        client (ArmoniKTasks): ArmoniKTasks instance for task management.
        task_ids (str): ID of the task to check.
    """
    for task_id in task_ids:
        tasks = client.get_task(task_id)
        if task_id == tasks.id:
            print(f"\nTask information for task ID {task_id} :\n")
            print(tasks)
        else:
            print(f"No task found with ID {task_id}")


def list_results(client: ArmoniKResults, result_filter: Filter):

    page = 0
    results = client.list_results(result_filter, page=page)
    while len(results[1]) > 0:
        for result in results[1]:
            print(f'Result ID: {result.result_id}')
        page += 1
        results = client.list_results(result_filter, page=page)

    print(f"\nTotal results: {results[0]}\n")


def main():

    parser = argparse.ArgumentParser(description="ArmoniK Admin CLI to perform administration tasks for ArmoniK", prog="akctl", epilog="EXAMPLES\n  akctl session -h\n\nLEARN MORE\n  Use 'akctl <command> <subcommand> --help' for more information", formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version="ArmoniK Admin CLI 0.0.1")
    parser.add_argument("--endpoint", default="localhost:5001", help="ArmoniK control plane endpoint")
    parser.add_argument("--ca", help="CA file for mutual TLS")
    parser.add_argument("--cert", help="Certificate for mutual TLS")
    parser.add_argument("--key", help="Private key for mutual TLS")
    parser.set_defaults(func=lambda _: parser.print_help())

    # TOP LEVEL COMMANDS
    subparsers = parser.add_subparsers(title='COMMANDS')

    session_parser = subparsers.add_parser('session', help='manage sessions')
    session_parser.set_defaults(func=lambda _: session_parser.print_help())
    task_parser = subparsers.add_parser('task', help='manage tasks')
    task_parser.set_defaults(func=lambda _: task_parser.print_help())
    result_parser = subparsers.add_parser('result', help='manage results')
    result_parser.set_defaults(func=lambda _: result_parser.print_help())
    partition_parser = subparsers.add_parser('partition', help='manage partitions')
    partition_parser.set_defaults(func=lambda _: partition_parser.print_help())
    config_parser = subparsers.add_parser('config', help='modify akconfig file (control plane URL, certificate for SSL, etc)')
    config_parser.set_defaults(func=lambda _: config_parser.print_help())

    # SESSION SUBCOMMAND
    session_subparsers = session_parser.add_subparsers(title='SESSION SUBCOMMANDS')

    # LIST SESSION
    list_session_parser = session_subparsers.add_parser('list', help='list sessions with specific filters')
    list_session_parser.add_argument("--running", dest="filter", default=None, action="store_const", const=SessionFieldFilter.STATUS == SESSION_STATUS_RUNNING, help="Select running sessions")
    list_session_parser.add_argument("--cancelled",  dest="filter", default=None, action="store_const", const=SessionFieldFilter.STATUS == SESSION_STATUS_CANCELLED, help="Select cancelled sessions")
    list_session_parser.set_defaults(func=lambda _: list_sessions(session_client, args.filter))

    # GET SESSION
    get_session_parser = session_subparsers.add_parser('get', help='get sessions with specific filters')
    get_session_parser.add_argument(dest="session_ids", nargs="+",  help="Select ID from session")
    get_session_parser.set_defaults(func=lambda args: check_session(session_client, args.session_ids))

    # # EDIT SESSION
    # edit_session_parser = session_subparsers.add_parser('edit', help='edit sessions with specific filters')
    # # edit_session_parser.set_defaults(func=lambda _: edit_session())

    # # DELETE SESSION
    # delete_session_parser = session_subparsers.add_parser('delete', help='delete sessions with specific filters')
    # # delete_session_parser.set_defaults(func=lambda _: delete_session())

    # # CREATE SESSION
    # create_session_parser = session_subparsers.add_parser('create', help='create sessions with specific filters')
    # # create_session_parser.set_defaults(func=lambda _: create_session())

    # TASK SUBCOMMAND
    task_subparsers = task_parser.add_subparsers(title='TASK SUBCOMMANDS')

    # LIST TASKS
    list_task_parser = task_subparsers.add_parser('list', help='List tasks with specific filters')
    list_task_parser.add_argument("--session-id",default=None, dest="session_id", help="Select ID from SESSION")
    list_task_parser.add_argument("--partition",default=None,  dest="partition_name", help="Select name of Partition")
    list_task_parser.set_defaults(func=lambda args: list_tasks(
    task_client,
    create_task_filter(args.partition_name, args.session_id, False) if args.partition_name and args.session_id else
    create_task_filter(args.partition_name, args.session_id, False) if args.session_id else
    create_task_filter(args.partition_name, args.session_id, False) if args.partition_name else
    None
))

    # CHECK TASK
    get_task_parser = task_subparsers.add_parser('get', help='List tasks with specific filters')
    get_task_parser.add_argument(dest="task_ids", nargs="+",  help="Select ID from TASK")
    get_task_parser.set_defaults(func=lambda args: check_task(task_client, args.task_ids))

 # TASK DURATION
    duration_task_parser = task_subparsers.add_parser('duration', help='Calculate total duration of tasks with specific filters')
    duration_task_parser.add_argument("--session-id", default=None, dest="session_id", help="Select ID from SESSION")
    duration_task_parser.add_argument("--partition", default=None, dest="partition_name", help="Select name of Partition")
    duration_task_parser.set_defaults(func=lambda args: calculate_tasks_duration(
    task_client,
    create_task_filter(args.partition_name, args.session_id, False) if args.partition_name and args.session_id else
    create_task_filter(args.partition_name, args.session_id, False) if args.session_id else
    create_task_filter(args.partition_name, args.session_id, False) if args.partition_name else
    None
))



    args = parser.parse_args()
    grpc_channel = create_channel(args.endpoint, args.ca, args.key, args.cert)
    task_client = ArmoniKTasks(grpc_channel)
    session_client = ArmoniKSessions(grpc_channel)
    # result_client = ArmoniKResults(grpc_channel)
    args.func(args)


if __name__ == '__main__':
    main()
