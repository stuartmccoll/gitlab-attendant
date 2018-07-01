import dateutil.parser
import pytz
import random

from datetime import datetime, timedelta

from api_calls import (
    assign_user_to_merge_request,
    get_all_open_merge_requests,
    get_all_project_members,
)


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
