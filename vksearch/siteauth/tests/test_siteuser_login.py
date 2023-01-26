from django.contrib.auth import get_user_model
from django.test import TestCase

from vksearch.settings import LOGIN_URL


class SiteUserLoginTest(TestCase):
    def setUp(self):
        self.credentials = {
            "username": "aurum",
            "password": "123Test456",
            "email": "test@example.com",
        }
        get_user_model().objects.create_user(**self.credentials)

    def test_siteuser_login_url_exists(self):
        resp = self.client.get(LOGIN_URL)
        self.assertEqual(resp.status_code, 200)

    def test_siteuser_login(self):
        response = self.client.post(LOGIN_URL, data=self.credentials)
        self.assertEqual(302, response.status_code)
        response = self.client.get(LOGIN_URL)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.context["user"].is_active)

    def tearDown(self):
        user = get_user_model().objects.get(username=self.credentials["username"])
        user.delete()
