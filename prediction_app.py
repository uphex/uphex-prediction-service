import flask
import json
import models.arima

app = flask.Flask(__name__)

@app.route("/", methods=["GET"])

def ping():
    return flask.Response("ok", content_type="text/plain", status=200)

@app.route("/", methods=["POST"])

def predict():
    app.debug = True

    input_values = [float(x) for x in flask.request.data.strip().split()]
    input_points = list(range(0, len(input_values)))
    input_series = {"point": input_points, "value": input_values}

    try:
        result = models.arima.forecast(input_series, 1)
        prediction = result["expected_value"][0]
        low, high = result["predictions"][0]
        output = {"forecast": prediction, "low": low, "high": high}

        return flask.Response(json.dumps(output), content_type="application/json", status=200)
    except(IndexError):
        return flask.Response("Invalid data", content_type="text/plain", status=400)
    except(TypeError):
        return flask.Response("Couldn't generate prediction", content_type="text/plain", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
