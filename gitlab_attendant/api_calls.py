from gitlab_attendant.log_handlers import logger
from gitlab_attendant.utils import (
    delete_request,
    get_request,
    post_request,
    put_request,
)


def get_all_projects(cli_args: dict) -> list:
    """
    Queries the GitLab API and returns all projects found.
    """
    request_url = f"http://{cli_args['ip_address']}/api/v4/projects"
    return get_request(request_url, cli_args["token"])


def get_project(cli_args: dict, project_id: int) -> dict:
    """
    Queries the GitLab API and returns details of the specified project.
    """
    request_url = (
        f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}"
    )
    return get_request(request_url, cli_args["token"])


def get_all_project_members(cli_args: dict, project_id: int) -> list:
    """
    Queries the GitLab API and returns all members of a project.
    """
    request_url = (
        f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}/members"
    )
    return get_request(request_url, cli_args["token"])


def get_user(cli_args: dict, user_id: int) -> dict:
    """
    Queries the GitLab API and returns details of the specified user.
    """
    request_url = f"http://{cli_args['ip_address']}/api/v4/users/{user_id}"
    return get_request(request_url, cli_args["token"])


def get_all_open_merge_requests(cli_args: dict) -> list:
    """
    Queries the GitLab API and returns all open merge requests.
    """
    request_url = (
        f"http://{cli_args['ip_address']}/api/v4/merge_requests?state=opened"
    )
    return get_request(request_url, cli_args["token"])


def assign_user_to_merge_request(
    cli_args: dict, project_id: int, merge_id: int, user_id: int
) -> dict:
    """
    Updates the merge request and assigns the given user id.
    """
    request_url = f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}/merge_requests/{merge_id}"
    body = {"assignee_id": user_id}
    return put_request(request_url, cli_args["token"], body)


def add_note_to_merge_request(
    cli_args: dict, project_id: int, merge_id: int, user_id: int, note_body: str
) -> dict:
    """
    Adds a note to the given merge request.
    """
    request_url = f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}/merge_requests/{merge_id}/notes"
    return post_request(request_url, cli_args["token"], note_body)


def add_note_to_issue(
    cli_args: dict, project_id: int, issue_id: int, note_body: str
) -> dict:
    """
    Adds a note to the given issue.
    """
    request_url = f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}/issues/{issue_id}/notes"
    return post_request(request_url, cli_args["token"], note_body)


def delete_merged_branches(cli_args: dict, project_id: int):
    """
    Queries the GitLab API and returns branches that have been merged.
    """

    request_url = f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}/repository/merged_branches"
    return delete_request(request_url, cli_args["token"])


def get_all_open_issues(cli_args: dict):
    """
    Queries the GitLab API and returns all open issues.
    """

    request_url = f"http://{cli_args['ip_address']}/api/v4/issues?state=opened"
    return get_request(request_url, cli_args["token"])


def assign_issue(cli_args: dict, project_id: int, issue_id: int, user_id: int):
    """
    Queries the GitLab API and assigns an issue to a specified user.
    """

    logger.info(
        f"Assigning issue {issue_id} of project {project_id} to user {user_id}..."
    )
    request_url = f"http://{cli_args['ip_address']}/api/v4/projects/{project_id}/issues/{issue_id}"
    body = {"assignee_ids": [user_id]}
    return put_request(request_url, cli_args["token"], body)
