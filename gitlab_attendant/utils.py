import requests
import sys
import traceback

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from gitlab_attendant.log_handlers import logger


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
        logger.debug(f"Making GET request to {request_url}...")
        response = session.get(request_url, headers={"Private-Token": token})
        logger.debug(
            f"Response status code from GET request to {request_url}: {response.status_code}"
        )
        logger.debug(
            f"Response body from GET request to {request_url}: {response.json()}"
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logger.error(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()


def put_request(request_url: str, token: str, body: dict) -> dict:
    """
    Wrapper for HTTP PUT requests.
    """

    try:
        logger.debug(
            f"Making PUT request to {request_url} with payload: {body}..."
        )
        response = requests.put(
            request_url, headers={"Private-Token": token}, data=body
        )
        logger.debug(
            f"Response status code from PUT request to {request_url}: {response.status_code}"
        )
        logger.debug(
            f"Response body from PUT request to {request_url}: {response.json()}"
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logger.error(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()


def post_request(request_url: str, token: str, body: dict) -> dict:
    """
    Wrapper for HTTP POST requests.
    """

    try:
        logger.debug(
            f"Making POST request to {request_url} with payload: {body}..."
        )
        response = requests.post(
            request_url, headers={"Private-Token": token}, data=body
        )
        logger.debug(
            f"Response status code from POST request to {request_url}: {response.status_code}"
        )
        logger.debug(
            f"Response body from POST request to {request_url}: {response.json()}"
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logger.error(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()


def delete_request(request_url: str, token: str) -> dict:
    """
    Wrapper for HTTP DELETE requests.
    """

    try:
        logger.debug(f"Making DELETE request to {request_url}...")
        response = requests.delete(
            request_url, headers={"Private-Token": token}
        )
        logger.debug(
            f"Response status code from DELETE request to {request_url}: {response.status_code}"
        )
        logger.debug(
            f"Response body from DELETE request to {request_url}: {response.json()}"
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logger.error(
            f"{traceback.extract_stack(None, 2)[0][2]} call to GitLab API failed with RequestException: {ex}"
        )
        sys.exit(1)

    return response.json()
