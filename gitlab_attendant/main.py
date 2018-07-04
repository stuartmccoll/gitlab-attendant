import sys

from argparse import ArgumentParser

from tasks import assign_open_merge_requests


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
        help="attend interval (ex. 1m, 10m, 1h)",
        default="10m",
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


def main():
    args = process_arguments()
    assign_open_merge_requests(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(f"Unhandled Exception occurred: {ex}.")
        print("Exiting GitLab Attendant process...")
        sys.exit(1)
