import json
import requests
import datetime


def refresh_auth():
    """
    The key for the Lightcast API must be refreshed hourly--this function 
    uses the saved username and secret in config.json to obtain a new one.
    """

    with open(f"auth.json", "r") as f:
        auth = json.load(f)


    retreived = auth.get("retreived", "1900-01-01")
    active_time = (
        datetime.datetime.now() 
        - datetime.datetime.fromisoformat(retreived)
    )

    # If it's been more than nine-tenths of an hour, get a new key
    if active_time > datetime.timedelta(hours=0.9):
        with open("config.json") as f:
            config = json.load(f)

            CLIENT_ID = config["username"]
            CLIENT_SECRET =  config["secret"]

        url = "https://auth.emsicloud.com/connect/token"

        payload = f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.request("POST", url, data=payload, headers=headers)

        auth = response.json()
        auth["retreived"] = datetime.datetime.now().isoformat()

        with open(f"auth.json", "w") as f:
            json.dump(auth, f)

    return auth
