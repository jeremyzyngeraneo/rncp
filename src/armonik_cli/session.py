from armonik.client.sessions import ArmoniKSessions
from armonik.common import Filter
import grpc


def list_sessions(client: ArmoniKSessions, session_filter: Filter):
    """
    List sessions with filter options

    Args:
        client (ArmoniKSessions): ArmoniKSessions instance for session management
        session_filter (Filter) : Filter for the session

    Returns:
        List[str]: A list of session IDs that match the filter criteria
    """
    result = []
    page = 0
    sessions = client.list_sessions(session_filter, page=page)

    while len(sessions[1]) > 0:
        for session in sessions[1]:
            result.append(session.session_id)
            print(f"Session ID: {session.session_id}")
        page += 1
        sessions = client.list_sessions(session_filter, page=page)

    print(f"\nNumber of sessions: {sessions[0]}\n")
    return result


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
            return sessions
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


def hello():
    return "Hello, Session!"
