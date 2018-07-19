import requests
import sys
import traceback

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def get_request(request_url: str, token: str) -> dict:
    """
    Wrapper for HTTP GET requests.
    """

    session = requests.Session()

    # Define the maximum number of retries and the time between each one
    retries = Retry(total=5, backoff_factor=0.1)

    # Mount both HTTP and HTTPS protocols
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(request_url, headers={"Private-Token": token})
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        print(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()


def put_request(request_url: str, token: str, body: dict) -> dict:
    """
    Wrapper for HTTP PUT requests.
    """

    try:
        response = requests.put(
            request_url, headers={"Private-Token": token}, data=body
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        print(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()


def post_request(request_url: str, token: str, body: dict) -> dict:
    """
    Wrapper for HTTP POST requests.
    """

    try:
        response = requests.post(
            request_url, headers={"Private-Token": token}, data=body
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        print(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()


def delete_request(request_url: str, token: str) -> dict:
    """
    Wrapper for HTTP DELETE requests.
    """

    try:
        response = requests.delete(
            request_url, headers={"Private-Token": token}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        print(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()
