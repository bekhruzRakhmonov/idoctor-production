from rest_framework import status
from rest_framework.test import APITestCase

class ExampleTestCase(APITestCase):
    def test_url_roor(self):
        url = reverse("users")
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

