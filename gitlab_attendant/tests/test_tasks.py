import mock
import pytz
import unittest

from datetime import datetime, timedelta

from gitlab_attendant.tasks import assign_open_merge_requests


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
