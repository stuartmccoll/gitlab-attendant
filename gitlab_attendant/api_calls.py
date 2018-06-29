from utils import get_request


def get_all_projects(cli_args: dict) -> list:
    """
    Queries the GitLab API and returns all projects found.
    """
    request_url = f"http://{cli_args['ip_address']}/api/v4/projects"
    return get_request(request_url, cli_args["token"])


def get_all_open_merge_requests(cli_args: dict) -> list:
    """
    Queries the GitLab API and returns all open merge requests.
    """
    request_url = (
        f"http://{cli_args['ip_address']}/api/v4/merge_requests?state=opened"
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
