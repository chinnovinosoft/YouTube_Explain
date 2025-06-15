import json
import requests
from custom_lib import greet, __version__

def lambda_handler(event, context):
    name = event.get("name", "User")
    message = greet(name)
    res = requests.get("https://api.github.com")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
            "lib_version": __version__,
            "github_status": res.status_code
        })
    }
