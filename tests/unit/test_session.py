#!/usr/bin/env python

"""Tests for `armonik_cli` package."""

import datetime

import armonik_cli.session as session
from .conftest import rpc_called, get_client
from armonik.client.sessions import SessionFieldFilter, ArmoniKSessions
from armonik.common import SessionStatus, TaskOptions


def test_hello():
    assert session.hello() == "Hello, Session!"


def test_list_sessions_all():
    sessions = session.list_sessions(get_client("Sessions"), None)
    assert rpc_called("Sessions", "ListSessions", 1)
    assert sessions == []


def test_list_sessions_running():
    sessions = session.list_sessions(
        get_client("Sessions"), SessionFieldFilter.STATUS == SessionStatus.RUNNING
    )
    assert rpc_called("Sessions", "ListSessions", 2)
    assert sessions == []


def test_list_sessions_cancelled():
    sessions = session.list_sessions(
        get_client("Sessions"), SessionFieldFilter.STATUS == SessionStatus.CANCELLED
    )
    assert rpc_called("Sessions", "ListSessions", 3)
    assert sessions == []


def test_cancel_single_session():
    session.cancel_sessions(get_client("Sessions"), ["session-id"])
    assert rpc_called("Sessions", "CancelSession")


def test_cancel_multiple_sessions():
    session.cancel_sessions(
        get_client("Sessions"), ["session-id1", "session-id2", "session-id3"]
    )
    assert rpc_called("Sessions", "CancelSession", 4)


def test_create_session():
    sessions_client: ArmoniKSessions = get_client("Sessions")
    default_task_options = TaskOptions(
        max_duration=datetime.timedelta(seconds=1), priority=1, max_retries=1
    )
    session_id = sessions_client.create_session(default_task_options)

    assert rpc_called("Sessions", "CreateSession")
    assert session_id == "session-id"


def test_get_session():
    sessions_client: ArmoniKSessions = get_client("Sessions")
    default_task_options = TaskOptions(
        max_duration=datetime.timedelta(seconds=1), priority=1, max_retries=1
    )
    session_id = sessions_client.create_session(default_task_options)
    session.check_session(get_client("Sessions"), ["session-id"])

    assert rpc_called("Sessions", "GetSession")
    assert session_id == "session-id"
