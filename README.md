# uphex-prediction-service
A service for making predictions on timeseries data.

Build with:

    docker build -t uphex/prediction-server .

Run with:

    docker run uphex/prediction-server python2 prediction_app.py

This will let you connect to the container directly at its Docker-assigned IP
address using the exposed ports.

If you'd rather just map those ports locally so that you don't have to look
up the container's IP address, you can do:

    docker run -p 4444:5000 uphex/prediction-server python prediction_app.py

and then connect to localhost:4444 to see the server running.
