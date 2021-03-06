import dateutil.parser
import pytz
import random

from datetime import datetime, timedelta

from gitlab_attendant.api_calls import (
    add_note_to_issue,
    add_note_to_merge_request,
    assign_issue,
    assign_user_to_merge_request,
    delete_merged_branches,
    get_all_open_merge_requests,
    get_all_project_members,
    get_all_projects,
    get_all_open_issues,
)
from gitlab_attendant.log_handlers import logger


def assign_open_merge_requests(cli_args: dict):
    """
    Find merge requests that have been open for longer than 24 hours with
    no assigned project member. Find possible project members for each
    merge request and assign them accordingly.
    """
    open_merge_requests = get_all_open_merge_requests(cli_args)

    # Discard open merge requests that are marked as work in progress
    [
        open_merge_requests.remove(merge_request)
        for merge_request in open_merge_requests
        if merge_request["work_in_progress"]
    ]

    current_timestamp = pytz.utc.localize(datetime.utcnow())

    # Discard open merge requests that aren't over 24 hours old
    [
        open_merge_requests.remove(merge_request)
        for merge_request in open_merge_requests
        if (
            current_timestamp
            - dateutil.parser.parse(merge_request["created_at"])
            < timedelta(1)
        )
    ]

    # Discard open merge requests that have an assignee
    [
        open_merge_requests.remove(merge_request)
        for merge_request in open_merge_requests
        if merge_request["assignee"]
    ]

    # If we have no applicable merge requests then exit the function
    if not open_merge_requests:
        pass

    # Get all project members
    all_project_members = {
        merge_request["project_id"]: get_all_project_members(
            cli_args, merge_request["project_id"]
        )
        for merge_request in open_merge_requests
    }

    secure_random = random.SystemRandom()

    # Differentiate clean project members, select one at random
    # and then assign them to the merge request
    for merge_request in open_merge_requests:
        clean_project_members = []
        for project_member in all_project_members[merge_request["project_id"]]:
            if project_member["id"] != merge_request["author"]["id"]:
                clean_project_members.append(project_member["id"])
        if clean_project_members:
            chosen_project_member = secure_random.choice(clean_project_members)
            assign_user_to_merge_request(
                cli_args,
                merge_request["project_id"],
                merge_request["iid"],
                chosen_project_member,
            )


def notify_stale_merge_request_assignees(cli_args: dict, days: int):
    """
    Find merge requests that have been open for longer than X days with
    an assigned project member. Add a comment to the open merge request
    referencing the assigned project member to notify them.
    """

    open_merge_requests = get_all_open_merge_requests(cli_args)

    # Discard open merge requests that are marked as work in progress
    [
        open_merge_requests.remove(merge_request)
        for merge_request in open_merge_requests
        if merge_request["work_in_progress"]
    ]

    current_timestamp = pytz.utc.localize(datetime.utcnow())

    # Discard open merge requests that aren't over X days old
    [
        open_merge_requests.remove(merge_request)
        for merge_request in open_merge_requests
        if (
            current_timestamp
            - dateutil.parser.parse(merge_request["created_at"])
            < timedelta(days)
        )
    ]

    # Discard open merge requests that don't have an assignee
    [
        open_merge_requests.remove(merge_request)
        for merge_request in open_merge_requests
        if not merge_request["assignee"]
    ]

    # If we have no applicable merge requests then exit the function
    if not open_merge_requests:
        pass

    [
        add_note_to_merge_request(
            cli_args,
            merge_request["project_id"],
            merge_request["iid"],
            merge_request["assignee"]["id"],
            {
                "body": f"Nudging user @{merge_request['assignee']['username']} - this merge request has been open since {merge_request['created_at']}. \n\n This could be merged without conflict."
            }
            if merge_request["merge_status"] == "can_be_merged"
            else {
                "body": f"Nudging user @{merge_request['assignee']['username']} - this merge request has been open since {merge_request['created_at']}. \n\n Merge conflicts exist."
            },
        )
        for merge_request in open_merge_requests
    ]


def remove_merged_branches(cli_args: dict):
    """
    Find and delete branches that have been merged.
    """

    projects = get_all_projects(cli_args)

    response_list = [
        delete_merged_branches(cli_args, project["id"]) for project in projects
    ]

    for response in response_list:
        if response["message"] != "202 Accepted":
            logger.error(
                f"Failed to delete branch, error: {response['message']}"
            )


def assign_project_members_to_issues(cli_args: dict):
    """
    Find issues that have not been assigned and then assign them to
    a project member selected at random.
    """

    all_open_issues = get_all_open_issues(cli_args)

    unassigned_open_issues = [
        unassigned_open_issue
        for unassigned_open_issue in all_open_issues
        if not unassigned_open_issue["assignees"]
        and not unassigned_open_issue["assignee"]
    ]

    if not unassigned_open_issues:
        pass

    # Get all project members
    all_project_members = {
        unassigned_open_issue["project_id"]: get_all_project_members(
            cli_args, unassigned_open_issue["project_id"]
        )
        for unassigned_open_issue in unassigned_open_issues
    }

    secure_random = random.SystemRandom()

    # Select a project member at random
    # and then assign them to the open issue
    for unassigned_open_issue in unassigned_open_issues:
        if all_project_members:
            chosen_project_member = secure_random.choice(
                all_project_members[unassigned_open_issue["project_id"]]
            )
            assign_issue(
                cli_args,
                unassigned_open_issue["project_id"],
                unassigned_open_issue["iid"],
                chosen_project_member["id"],
            )


def notify_issue_assignees(cli_args: dict, days: int):
    """
    Find assigned issues that are overdue and due within X days,
    then notify the issue assignees accordingly.
    """

    all_open_issues = get_all_open_issues(cli_args)

    # Filter out unassigned issues
    assigned_open_issues = [
        assigned_open_issue
        for assigned_open_issue in all_open_issues
        if assigned_open_issue["assignees"] or assigned_open_issue["assignee"]
    ]

    if not assigned_open_issues:
        pass

    # Filter out assigned issues without due dates
    [
        assigned_open_issues.remove(open_issue)
        for open_issue in assigned_open_issues
        if not open_issue["due_date"]
    ]

    current_timestamp = pytz.utc.localize(datetime.utcnow())

    # Filter issues that are overdue into a new list
    overdue_issues = [
        open_issue
        for open_issue in assigned_open_issues
        if (
            (
                current_timestamp
                - pytz.utc.localize(
                    dateutil.parser.parse(open_issue["due_date"])
                )
            ).days
            > 0
        )
    ]

    # Filter issues that are due in under X days into a new list
    due_issues = [
        open_issue
        for open_issue in assigned_open_issues
        if (
            pytz.utc.localize(dateutil.parser.parse(open_issue["due_date"]))
            - current_timestamp
            < timedelta(days)
            and (
                pytz.utc.localize(dateutil.parser.parse(open_issue["due_date"]))
                - current_timestamp
            ).days
            > 0
        )
    ]

    [
        add_note_to_issue(
            cli_args,
            overdue_issue["project_id"],
            overdue_issue["iid"],
            {
                "body": f"Nudging user @{overdue_issue['assignee']['username']} - this issue was due on {overdue_issue['due_date']}."
            }
            if overdue_issue["assignee"]
            else {
                "body": f"Nudging users {', '.join(str('@{}'.format(user['username'])) for user in overdue_issue['assignees'])} - this issue was due on {overdue_issue['due_date']}."
            },
        )
        for overdue_issue in overdue_issues
    ]

    [
        add_note_to_issue(
            cli_args,
            due_issue["project_id"],
            due_issue["iid"],
            {
                "body": f"Nudging user @{due_issue['assignee']['username']} - this issue is due on {due_issue['due_date']}."
            }
            if due_issue["assignee"]
            else {
                "body": f"Nudging users {', '.join(str('@{}'.format(user['username'])) for user in due_issue['assignees'])} - this issue is due on {due_issue['due_date']}."
            },
        )
        for due_issue in due_issues
    ]
