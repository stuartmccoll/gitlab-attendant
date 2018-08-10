import schedule
import sys
import time

from argparse import ArgumentParser

from gitlab_attendant.log_handlers import logger
from gitlab_attendant.tasks import (
    assign_project_members_to_issues,
    assign_open_merge_requests,
    notify_issue_assignees,
    notify_stale_merge_request_assignees,
    remove_merged_branches,
)


def process_arguments() -> dict:
    parser = ArgumentParser(prog="gitlab-attendant")
    parser.add_argument(
        "--ip",
        dest="ip",
        help="specify IP address of the GitLab repository",
        required=True,
    )
    parser.add_argument(
        "--interval",
        dest="interval",
        help="task scheduler interval in hours (ex. 1, 10)",
        default="24",
        required=False,
    )
    parser.add_argument(
        "--token",
        dest="token",
        help="GitLab API personal access token",
        required=True,
    )

    args = parser.parse_args()

    return {
        "ip_address": args.ip,
        "interval": args.interval,
        "token": args.token,
    }


def tasks(args):
    """
    Function calls to the tasks that the GitLab Attendant
    is capable of running.
    """
    logger.info("GitLab Attendant has woken up...")
    logger.info(
        f"GitLab Attendant will begin attending to GitLab instance at {args['ip_address']}..."
    )

    assign_project_members_to_issues(args)
    assign_open_merge_requests(args)
    notify_issue_assignees(args, 7)
    notify_stale_merge_request_assignees(args, 7)
    remove_merged_branches(args)


def main():
    """
	Entrypoint to the application.
	"""
    args = process_arguments()
    schedule.every(int(args["interval"])).hours.do(tasks, args)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(f"Unhandled Exception occurred: {ex}.")
        print("Exiting GitLab Attendant process...")
        sys.exit(1)
