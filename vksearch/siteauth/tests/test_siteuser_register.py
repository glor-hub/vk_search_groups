from django.contrib.auth import get_user_model
from django.test import TestCase

REGISTER_URL = "/siteauth/signup/"


class SiteUserRegisterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_data = {
            "username": "boris",
            "email": "rty@comp.local",
            "password1": "PortPort",
            "password2": "PortPort",
        }
        cls.incorrect_user_data = {
            "username": "boris",
            "email": "boris@comp.local",
            "password1": "PortPort",
            "password2": "pass",
        }

    def test_siteuser_register_url_exists(self):
        resp = self.client.get(REGISTER_URL)
        self.assertEqual(resp.status_code, 200)

    def test_siteuser_register(self):
        response = self.client.post(REGISTER_URL)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.context["user"].is_anonymous)
        response = self.client.post(REGISTER_URL, data=self.user_data)
        self.assertEqual(302, response.status_code)

        new_user = get_user_model().objects.get(username=self.user_data["username"])
        self.assertEqual(self.user_data["email"], new_user.email)

    def test_siteuser_fail_register(self):
        response = self.client.post(REGISTER_URL, data=self.incorrect_user_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(
            response, "form", "password2", ("The two password fields didn’t match.")
        )
        self.assertIn(
            ("The two password fields didn’t match."), response.content.decode()
        )
