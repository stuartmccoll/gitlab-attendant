# GitLab Attendant

[![Build Status](https://travis-ci.org/stuartmccoll/gitlab-attendant.svg?branch=master)](https://travis-ci.org/stuartmccoll/gitlab-attendant) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

The GitLab Attendant is a bot that will tidy and attend to repositories on a specified GitLab installation at a scheduled basis. Currently the bot is capable of removing merged branches, assigning project members to open issues, assigning project members to open merge requests, notifying issue assignees of due or overdue issues, and notifying assignees of stale merge requests.

In order to use the GitLab Attendant fully, you should create a new account within the specified GitLab installation with privileges that will allow the bot to read and write any changes necessary to branches, merge requests, issues, etc. The personal access token for this account should then be entered in the `token` paramter when calling the bot from the command line.

**Python 3.6** or **Python 3.7** are required to run this utility.

## Installation

This utility can be installed through [pip](https://pypi.org/project/pip/) by running the following command:

```shell
pip install gitlab-attendant
```

## Usage

```shell
gitlab-attendant --ip localhost --interval 7 --token TOKEN

Options:
  --ip          The IP address of the GitLab installation.
  --interval    task scheduler interval in hours (ex. 1, 10) [default: 24]
  --token       GitLab personal access token.
```

This will run the GitLab Attendant process, which will begin attending to the specified GitLab installation at the first interval specified.

## Tests

Tests for this project utilise the [Pytest](https://pypi.org/project/pytest/) framework. To run the existing suite of unit tests run the following command within the root directory:

```shell
pytest
```

## Notes

All Python code has been formatted by [Black](https://github.com/ambv/black), 'the uncompromising Python code formatter'.

Type checking has been provided by [Pyre](https://pyre-check.org/).

Continuous integration is handled by [Travis CI](https://travis-ci.org/).

## License

See [LICENSE.md](LICENSE.md).
