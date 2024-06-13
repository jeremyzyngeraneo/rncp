from armonik.client.tasks import ArmoniKTasks, TaskFieldFilter
from armonik.common import Filter
from armonik.common.enumwrapper import (
    TASK_STATUS_CREATING,
)


def create_task_filter(partition: str, session_id: str, creating: bool) -> Filter:
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
        tasks_filter = (TaskFieldFilter.SESSION_ID == session_id) & (
            TaskFieldFilter.PARTITION_ID == partition
        )
    elif partition:
        tasks_filter = TaskFieldFilter.PARTITION_ID == partition
    elif creating and creating:
        tasks_filter = (TaskFieldFilter.SESSION_ID == session_id) & (
            TaskFieldFilter.STATUS == TASK_STATUS_CREATING
        )
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
            print(f"Task ID: {task.id}")
        page += 1
        tasks = client.list_tasks(task_filter, page=page)

    print(f"\nTotal tasks: {tasks[0]}\n")


def get_task_durations(client: ArmoniKTasks, task_filter: Filter):
    """
    Get task durations per partition

    Args:
        client (ArmoniKTasks): Instance of ArmoniKTasks
        task_filter (Filter): Filter for the task
    """
    tasks = client.list_tasks(task_filter)
    durations = {}

    for task in tasks[1]:
        partition = task.options.partition_id
        duration = (task.ended_at - task.started_at).total_seconds()

        if partition in durations:
            durations[partition] += duration
        else:
            durations[partition] = duration

    for partition, duration in durations.items():
        print(f"Partition: {partition} = {duration} secondes")


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


def hello():
    return "Hello, Task!"
