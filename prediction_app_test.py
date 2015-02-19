import unittest
import json

import prediction_app

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.app = prediction_app.app.test_client()

    def test_forecast(self):
        response = self.app.post("/", data="10 20 30 40 50 60")
        data = json.loads(response.data)

        assert data["forecast"] == 70.0

    def test_invalid_forecast(self):
        response = self.app.post("/", data="10 20 30")

        assert response.status == "500 INTERNAL SERVER ERROR"

if __name__ == "__main__":
    unittest.main()
