import requests
import json


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def fetch_approaching_trains():
    param = {"approaching": "true"}
    response = requests.get("http://localhost:8080/trains", params=param)
    return response.json()


def fetch_trains():
    response = requests.get("http://localhost:8080/trains")
    return response.json()


def fetch_train_line(line: str):
    response = requests.get("http://localhost:8080/trains/" + line)
    return response.json()


if __name__ == "__main__":
    trains = fetch_approaching_trains()
    jprint(trains)
