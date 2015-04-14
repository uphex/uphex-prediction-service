import unittest
import json

import prediction_app

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.app = prediction_app.app.test_client()

    def test_prediction(self):
        response = self.app.post("/", data="10 20 30 40 50 60")
        data = json.loads(response.data)

        assert data["forecast"] == 70.0

    def test_prediction_check_nan(self):
        response = self.app.post("/", data=("242.0 267.0 756.0 1101.0 1211.0 1181.0 929.0 271.0 381.0 1212.0 "
                                            "1277.0 1265.0 1207.0 955.0 233.0 268.0 1020.0 1049.0 1140.0 1185.0 "
                                            "925.0 251.0 286.0 1020.0 1187.0 1094.0 1082.0 863.0 214.0 305.0 972.0 "
                                            "1014.0 1046.0 1046.0 929.0 213.0 285.0 1119.0 1224.0 1140.0 1062.0 "
                                            "862.0 234.0 273.0 1099.0"))
        data = json.loads(response.data)

        assert data["forecast"] == data["forecast"]
        assert data["low"] == data["low"]
        assert data["high"] == data["high"]

    def test_empty_prediction(self):
        response = self.app.post("/", data="")

        assert response.status == "400 BAD REQUEST"

    def test_bad_prediction(self):
        response = self.app.post("/", data="10 20 30")

        assert response.status == "500 INTERNAL SERVER ERROR"

if __name__ == "__main__":
    unittest.main()
