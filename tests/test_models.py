import unittest
from unittest.mock import patch, Mock
from cumulus import Cumulus
from cumulus.models import BaseModel, Revision, Root

TEST_URL = 'https://localhost:8765'
TEST_AUTH = ('cumulus', 'something')


class TestBaseModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = Cumulus(url=TEST_URL, auth=TEST_AUTH)
        cls.base_model = BaseModel(cls.api, endpoint='')
        cls.rev = "custom_rev"

    def test__make_path_empty(self):
        path = self.base_model._make_path("")
        self.assertEqual(path, self.base_model.url)

    def test__make_path_target(self):
        path = self.base_model._make_path("endpoint")
        expected = f'{self.base_model.url}/endpoint'
        self.assertEqual(path, expected)

    @patch(
        'cumulus.base.Request.get',
        return_value=dict()
    )
    def test_get(self, get_request: Mock):
        get = self.base_model.get()
        self.assertIsInstance(get, dict)
        get_request.assert_called_once_with(
            params={}
        )

    @patch(
        'cumulus.base.Request.patch',
        return_value=dict()
    )
    def test_patch(self, patch_request: Mock):
        patch = self.base_model.patch(rev=self.rev, data={})
        self.assertIsInstance(patch, dict)
        patch_request.assert_called_once_with(
            data={}, params={"rev": self.rev}
        )

    @patch(
        'cumulus.base.Request.post',
        return_value=dict()
    )
    def test_patch(self, post_request: Mock):
        post = self.base_model.post()
        self.assertIsInstance(post, dict)
        post_request.assert_called_once_with(
            params={}
        )

    @patch(
        'cumulus.base.Request.delete',
        return_value=dict()
    )
    def test_delete(self, delete_request: Mock):
        delete = self.base_model.delete(rev=self.rev)
        self.assertIsInstance(delete, dict)
        delete_request.assert_called_once_with(
            params={"rev": self.rev}
        )


class TestRevision(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = Cumulus(url=TEST_URL, auth=TEST_AUTH)
        cls.revision = Revision(cls.api, endpoint="revision")

    @patch(
        'cumulus.base.Request.post',
        return_value={
            "1": {
                "state": "pending",
                "transition": {
                    "issue": {},
                    "progress": ""
                }
            }
        }
    )
    def test_create(self, _):
        created = self.revision.create()
        self.assertIsInstance(created, dict)
        self.assertEqual(self.revision.rev, "1")

    @patch(
        'cumulus.base.Request.patch',
        return_value=dict()
    )
    def test_apply(self, patch: Mock):
        self.revision.rev = "1"
        applied = self.revision.apply()
        self.assertIsInstance(applied, dict)
        patch.assert_called_once_with(
            data={"state": "apply",
                  "auto-prompt": {"ays": "ays_yes"}}
        )

    @patch(
        'cumulus.models.Revision.refresh',
        return_value={
            "state": "applied",
            "transition": {
                "issue": {},
                "progress": ""
            }
        }
    )
    def test_is_applied_success(self, _):
        applied = self.revision.is_applied(retries=1, sleep_time=0)
        self.assertTrue(applied)

    @patch(
        'cumulus.models.Revision.refresh',
        return_value={
            "state": "invalid",
            "transition": {
                "issue": {
                    "0": {
                        "code": "config_invalid"
                    }
                },
                "progress": "Invalid config"
            }
        }
    )
    def test_is_applied_failure(self, _):
        not_applied = self.revision.is_applied(retries=1, sleep_time=0)
        self.assertFalse(not_applied)

    @patch(
        'cumulus.models.BaseModel.get',
        return_value=dict()
    )
    def test_refresh(self, get: Mock):
        self.revision.rev = "1"
        refreshed = self.revision.refresh()
        self.assertIsInstance(refreshed, dict)
        get.assert_called_once_with(self.revision.rev)

    @patch(
        'cumulus.models.BaseModel.get',
        return_value=dict()
    )
    def test_switch(self, get: Mock):
        rev = "2"
        switched = self.revision.switch(rev)
        self.assertIsInstance(switched, dict)
        self.assertEqual(self.revision.rev, rev)
        get.assert_called_once_with(rev)


class TestRoot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = Cumulus(url=TEST_URL, auth=TEST_AUTH)
        cls.root = Root(cls.api, endpoint="")

    @patch(
        'cumulus.models.BaseModel.get',
        return_value=dict()
    )
    def test_diff(self, get: Mock):
        revision_a = "a"
        diff = self.root.diff(revision_a=revision_a)
        self.assertIsInstance(diff, dict)
        get.assert_called_once_with(
            endpoint_params={
                "rev": revision_a,
                "diff": "applied",
                "filled": False
            }
        )
