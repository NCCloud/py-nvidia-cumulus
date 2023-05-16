import unittest
from unittest.mock import patch, Mock
from cumulus import Cumulus

TEST_URL = 'https://localhost:8765'
TEST_AUTH = ('cumulus', 'something')


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = Cumulus(url=TEST_URL, auth=TEST_AUTH)

    def test_format_url(self):
        self.assertTrue(self.api.url, f'{TEST_URL}/nvue_v1')

    @patch(
        'cumulus.base.Request.get',
        return_value=dict()
    )
    def test_health(self, get: Mock):
        health = self.api.health()
        self.assertIsInstance(health, dict)
        get.assert_called_once()
