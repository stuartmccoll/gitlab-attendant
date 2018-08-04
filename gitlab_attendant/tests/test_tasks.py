import contextlib
import mock
import pytz
import unittest

from datetime import datetime, timedelta
from io import StringIO

from gitlab_attendant.tasks import (
    assign_open_merge_requests,
    assign_project_members_to_issues,
    notify_issue_assignees,
    notify_stale_merge_request_assignees,
    remove_merged_branches,
)


class TestTasks(unittest.TestCase):
    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 24 hours old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(2)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "assignee": None,
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
            }
        ]

        mock_get_project_members.return_value = [{"id": 5}]

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_assign_user_to_merge.called, True)
        self.assertEqual(mock_assign_user_to_merge.call_count, 1)
        mock_assign_user_to_merge.assert_called_with(cli_args, 1, 1, 5)

    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests_no_merge_requests(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_open_merge_requests.return_value = []

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_get_project_members.called, False)
        self.assertEqual(mock_get_project_members.call_count, 0)
        self.assertEqual(mock_assign_user_to_merge.called, False)
        self.assertEqual(mock_assign_user_to_merge.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests_work_in_progress(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_open_merge_requests.return_value = [{"work_in_progress": True}]

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_get_project_members.called, False)
        self.assertEqual(mock_get_project_members.call_count, 0)
        self.assertEqual(mock_assign_user_to_merge.called, False)
        self.assertEqual(mock_assign_user_to_merge.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests_not_stale(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be less than 24 hours old
        created_at = pytz.utc.localize(datetime.utcnow())

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "assignee": None,
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
            }
        ]

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_get_project_members.called, False)
        self.assertEqual(mock_get_project_members.call_count, 0)
        self.assertEqual(mock_assign_user_to_merge.called, False)
        self.assertEqual(mock_assign_user_to_merge.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests_already_assigned(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be more than 24 hours old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(2)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "assignee": {"id": 2},
            }
        ]

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_get_project_members.called, False)
        self.assertEqual(mock_get_project_members.call_count, 0)
        self.assertEqual(mock_assign_user_to_merge.called, False)
        self.assertEqual(mock_assign_user_to_merge.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests_no_project_members(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 24 hours old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(2)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "assignee": None,
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
            }
        ]

        mock_get_project_members.return_value = []

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_assign_user_to_merge.called, False)
        self.assertEqual(mock_assign_user_to_merge.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.assign_user_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_assign_open_merge_requests_same_project_member(
        self,
        mock_open_merge_requests,
        mock_get_project_members,
        mock_assign_user_to_merge,
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 24 hours old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(2)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "assignee": None,
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
            }
        ]

        mock_get_project_members.return_value = [{"id": 1}]

        assign_open_merge_requests(cli_args)

        self.assertEqual(mock_assign_user_to_merge.called, False)
        self.assertEqual(mock_assign_user_to_merge.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.add_note_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_notify_stale_merge_request_assignees(
        self, mock_open_merge_requests, mock_add_note_to_merge_request
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 6 days old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(7)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
                "assignee": {"id": 1, "username": "test-user"},
                "merge_status": "can_be_merged",
            }
        ]

        notify_stale_merge_request_assignees(cli_args, 5)

        self.assertEqual(mock_add_note_to_merge_request.called, True)
        self.assertEqual(mock_add_note_to_merge_request.call_count, 1)
        mock_add_note_to_merge_request.assert_called_with(
            cli_args,
            1,
            1,
            1,
            {
                "body": f"Nudging user @test-user - this merge request has been open since {created_at.isoformat()}. \n\n This could be merged without conflict."
            },
        )

    @mock.patch("gitlab_attendant.tasks.add_note_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_notify_stale_merge_request_assignees_merge_conflicts(
        self, mock_open_merge_requests, mock_add_note_to_merge_request
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 6 days old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(7)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
                "assignee": {"id": 1, "username": "test-user"},
                "merge_status": "cannot_be_merged",
            }
        ]

        notify_stale_merge_request_assignees(cli_args, 5)

        self.assertEqual(mock_add_note_to_merge_request.called, True)
        self.assertEqual(mock_add_note_to_merge_request.call_count, 1)
        mock_add_note_to_merge_request.assert_called_with(
            cli_args,
            1,
            1,
            1,
            {
                "body": f"Nudging user @test-user - this merge request has been open since {created_at.isoformat()}. \n\n Merge conflicts exist."
            },
        )

    @mock.patch("gitlab_attendant.tasks.add_note_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_notify_stale_merge_request_assignees_no_assignee(
        self, mock_open_merge_requests, mock_add_note_to_merge_request
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 6 days old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(7)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
                "assignee": None,
                "merge_status": "cannot_be_merged",
            }
        ]

        notify_stale_merge_request_assignees(cli_args, 5)

        self.assertEqual(mock_add_note_to_merge_request.called, False)
        self.assertEqual(mock_add_note_to_merge_request.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.add_note_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_notify_stale_merge_request_assignees_work_in_progress(
        self, mock_open_merge_requests, mock_add_note_to_merge_request
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 6 days old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(7)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": True,
                "created_at": created_at.isoformat(),
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
                "assignee": {"id": 1, "username": "test-user"},
                "merge_status": "cannot_be_merged",
            }
        ]

        notify_stale_merge_request_assignees(cli_args, 5)

        self.assertEqual(mock_add_note_to_merge_request.called, False)
        self.assertEqual(mock_add_note_to_merge_request.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.add_note_to_merge_request")
    @mock.patch("gitlab_attendant.tasks.get_all_open_merge_requests")
    def test_notify_stale_merge_request_assignees_not_stale(
        self, mock_open_merge_requests, mock_add_note_to_merge_request
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        # Set the created_at date to be over 24 hours old
        created_at = pytz.utc.localize(datetime.utcnow()) - timedelta(2)

        mock_open_merge_requests.return_value = [
            {
                "work_in_progress": False,
                "created_at": created_at.isoformat(),
                "project_id": 1,
                "author": {"id": 1},
                "iid": 1,
                "assignee": {"id": 1, "username": "test-user"},
                "merge_status": "cannot_be_merged",
            }
        ]

        notify_stale_merge_request_assignees(cli_args, 5)

        self.assertEqual(mock_add_note_to_merge_request.called, False)
        self.assertEqual(mock_add_note_to_merge_request.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.delete_merged_branches")
    @mock.patch("gitlab_attendant.tasks.get_all_projects")
    def test_remove_merged_branches(
        self, mock_get_all_projects, mock_delete_merged_branches
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_get_all_projects.return_value = [{"id": 1}]

        mock_delete_merged_branches.side_effect = [{"message": "202 Accepted"}]

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            remove_merged_branches(cli_args)

        self.assertEqual(mock_delete_merged_branches.called, True)
        self.assertEqual(mock_delete_merged_branches.call_count, 1)
        self.assertEqual(temp_stdout.getvalue().strip(), "")

    @mock.patch("gitlab_attendant.tasks.logger.error")
    @mock.patch("gitlab_attendant.tasks.delete_merged_branches")
    @mock.patch("gitlab_attendant.tasks.get_all_projects")
    def test_remove_merged_branches_with_errors(
        self, mock_get_all_projects, mock_delete_merged_branches, mock_log_error
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_get_all_projects.return_value = [{"id": 1}, {"id": 2}]

        mock_delete_merged_branches.side_effect = [
            {"message": "202 Accepted"},
            {"message": "Something went wrong..."},
        ]

        remove_merged_branches(cli_args)

        self.assertEqual(mock_delete_merged_branches.called, True)
        self.assertEqual(mock_delete_merged_branches.call_count, 2)
        self.assertEqual(mock_log_error.called, True)
        self.assertEqual(mock_log_error.call_count, 1)

    @mock.patch("gitlab_attendant.tasks.assign_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_assign_project_members_to_open_issues_multiple_project_members(
        self, mock_all_open_issues, mock_all_project_members, mock_assign_issue
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": {"id": 1},
                "assignees": [],
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": None,
                "assignees": [],
            },
        ]

        mock_all_project_members.return_value = [
            {"id": 1, "iid": 1},
            {"id": 2, "iid": 2},
        ]

        assign_project_members_to_issues(cli_args)

        self.assertEqual(mock_assign_issue.called, True)
        self.assertEqual(mock_assign_issue.call_count, 1)
        mock_assign_issue.assert_called_with(cli_args, 1, mock.ANY, mock.ANY)

    @mock.patch("gitlab_attendant.tasks.assign_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_assign_project_members_to_open_issues_single_project_member(
        self, mock_all_open_issues, mock_all_project_members, mock_assign_issue
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [{"id": 1}, {"id": 2}],
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": None,
                "assignees": [],
            },
        ]

        mock_all_project_members.return_value = [{"id": 1, "iid": 1}]

        assign_project_members_to_issues(cli_args)

        self.assertEqual(mock_assign_issue.called, True)
        self.assertEqual(mock_assign_issue.call_count, 1)
        mock_assign_issue.assert_called_with(cli_args, 1, 2, 1)

    @mock.patch("gitlab_attendant.tasks.assign_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_assign_project_members_to_open_issues_all_assigned(
        self, mock_all_open_issues, mock_all_project_members, mock_assign_issue
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [{"id": 1}, {"id": 2}],
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": {"id": 1},
                "assignees": [],
            },
        ]

        mock_all_project_members.return_value = [{"id": 1, "iid": 1}]

        assign_project_members_to_issues(cli_args)

        self.assertEqual(mock_assign_issue.called, False)
        self.assertEqual(mock_assign_issue.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.assign_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_project_members")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_assign_project_members_to_open_issues_no_open_issues(
        self, mock_all_open_issues, mock_all_project_members, mock_assign_issue
    ):
        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        mock_all_open_issues.return_value = []

        assign_project_members_to_issues(cli_args)

        self.assertEqual(mock_all_project_members.called, False)
        self.assertEqual(mock_all_project_members.call_count, 0)
        self.assertEqual(mock_assign_issue.called, False)
        self.assertEqual(mock_assign_issue.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.add_note_to_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_notify_issue_assignees(
        self, mock_all_open_issues, mock_add_note_to_issue
    ):
        due_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) + timedelta(2), "%Y-%m-%d"
        )
        overdue_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) - timedelta(8), "%Y-%m-%d"
        )

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [
                    {"id": 1, "username": "test-user"},
                    {"id": 2, "username": "admin-user"},
                ],
                "due_date": due_date,
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": {"id": 1, "username": "developer"},
                "assignees": [],
                "due_date": overdue_date,
            },
        ]

        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        notify_issue_assignees(cli_args, 7)

        self.assertEqual(mock_add_note_to_issue.called, True)
        calls = [
            mock.call(
                cli_args,
                1,
                2,
                {
                    "body": f"Nudging user @developer - this issue was due on {overdue_date}."
                },
            ),
            mock.call(
                cli_args,
                1,
                1,
                {
                    "body": f"Nudging users @test-user, @admin-user - this issue is due on {due_date}."
                },
            ),
        ]
        mock_add_note_to_issue.assert_has_calls(calls)
        self.assertEqual(mock_add_note_to_issue.call_count, 2)

    @mock.patch("gitlab_attendant.tasks.add_note_to_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_notify_issue_assignees_no_assignees(
        self, mock_all_open_issues, mock_add_note_to_issue
    ):
        due_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) + timedelta(2), "%Y-%m-%d"
        )
        overdue_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) - timedelta(8), "%Y-%m-%d"
        )

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [],
                "due_date": due_date,
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": None,
                "assignees": [],
                "due_date": overdue_date,
            },
        ]

        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        notify_issue_assignees(cli_args, 7)

        self.assertEqual(mock_add_note_to_issue.called, False)
        self.assertEqual(mock_add_note_to_issue.call_count, 0)

    @mock.patch("gitlab_attendant.tasks.add_note_to_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_notify_issue_assignees_singe_assignee(
        self, mock_all_open_issues, mock_add_note_to_issue
    ):
        due_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) + timedelta(2), "%Y-%m-%d"
        )
        overdue_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) - timedelta(8), "%Y-%m-%d"
        )

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": {"id": 1, "username": "developer"},
                "assignees": [],
                "due_date": due_date,
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": {"id": 2, "username": "tester"},
                "assignees": [],
                "due_date": overdue_date,
            },
        ]

        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        notify_issue_assignees(cli_args, 7)

        calls = [
            mock.call(
                cli_args,
                1,
                2,
                {
                    "body": f"Nudging user @tester - this issue was due on {overdue_date}."
                },
            ),
            mock.call(
                cli_args,
                1,
                1,
                {
                    "body": f"Nudging user @developer - this issue is due on {due_date}."
                },
            ),
        ]

        self.assertEqual(mock_add_note_to_issue.called, True)
        mock_add_note_to_issue.assert_has_calls(calls)
        self.assertEqual(mock_add_note_to_issue.call_count, 2)

    @mock.patch("gitlab_attendant.tasks.add_note_to_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_notify_issue_assignees_multiple_assignees(
        self, mock_all_open_issues, mock_add_note_to_issue
    ):
        due_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) + timedelta(2), "%Y-%m-%d"
        )
        overdue_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) - timedelta(8), "%Y-%m-%d"
        )

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [
                    {"id": 1, "username": "developer"},
                    {"id": 2, "username": "tester"},
                ],
                "due_date": due_date,
            },
            {
                "id": 2,
                "iid": 2,
                "project_id": 1,
                "assignee": None,
                "assignees": [
                    {"id": 3, "username": "test-user"},
                    {"id": 4, "username": "admin-user"},
                ],
                "due_date": overdue_date,
            },
        ]

        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        notify_issue_assignees(cli_args, 7)

        calls = [
            mock.call(
                cli_args,
                1,
                2,
                {
                    "body": f"Nudging users @test-user, @admin-user - this issue was due on {overdue_date}."
                },
            ),
            mock.call(
                cli_args,
                1,
                1,
                {
                    "body": f"Nudging users @developer, @tester - this issue is due on {due_date}."
                },
            ),
        ]

        self.assertEqual(mock_add_note_to_issue.called, True)
        mock_add_note_to_issue.assert_has_calls(calls)
        self.assertEqual(mock_add_note_to_issue.call_count, 2)

    @mock.patch("gitlab_attendant.tasks.add_note_to_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_notify_issue_assignees_no_overdue_issues(
        self, mock_all_open_issues, mock_add_note_to_issue
    ):
        due_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) + timedelta(2), "%Y-%m-%d"
        )

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [
                    {"id": 1, "username": "developer"},
                    {"id": 2, "username": "tester"},
                ],
                "due_date": due_date,
            }
        ]

        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        notify_issue_assignees(cli_args, 7)

        self.assertEqual(mock_add_note_to_issue.called, True)
        mock_add_note_to_issue.assert_called_with(
            cli_args,
            1,
            1,
            {
                "body": f"Nudging users @developer, @tester - this issue is due on {due_date}."
            },
        )
        self.assertEqual(mock_add_note_to_issue.call_count, 1)

    @mock.patch("gitlab_attendant.tasks.add_note_to_issue")
    @mock.patch("gitlab_attendant.tasks.get_all_open_issues")
    def test_notify_issue_assignees_no_due_issues(
        self, mock_all_open_issues, mock_add_note_to_issue
    ):
        due_date = datetime.strftime(
            pytz.utc.localize(datetime.utcnow()) + timedelta(10), "%Y-%m-%d"
        )

        mock_all_open_issues.return_value = [
            {
                "id": 1,
                "iid": 1,
                "project_id": 1,
                "assignee": None,
                "assignees": [
                    {"id": 1, "username": "developer"},
                    {"id": 2, "username": "tester"},
                ],
                "due_date": due_date,
            }
        ]

        cli_args = {"ip_address": "localhost", "interval": 1, "token": "test"}

        notify_issue_assignees(cli_args, 7)

        self.assertEqual(mock_add_note_to_issue.called, False)
        self.assertEqual(mock_add_note_to_issue.call_count, 0)
