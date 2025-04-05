import requests

claim_id = "CLM12345"

payload = {"claim_id": claim_id}

status = requests.post("http://127.0.0.1:8000/claim/status", json=payload)
date = requests.post("http://127.0.0.1:8000/claim/date", json=payload)
comment = requests.post("http://127.0.0.1:8000/claim/comment", json=payload)

print("Claim Status:", status.json()['status'])
print("Claim Date:", date.json()['claim_date'])
print("Latest Comment:", comment.json()['latest_comment'])
