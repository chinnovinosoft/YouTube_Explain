from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()
claims_db = {
    "CLM12345": {
        "status": "Approved",
        "claim_date": "2024-12-01",
        "latest_comment": "Claim approved and amount disbursed on 2024-12-10"
    },
    "CLM54321": {
        "status": "Pending",
        "claim_date": "2025-02-15",
        "latest_comment": "Documents under review. Awaiting assessor report."
    },
    "CLM99999": {
        "status": "Rejected",
        "claim_date": "2025-01-20",
        "latest_comment": "Claim rejected due to policy expiration."
    }
}

class ClaimRequest(BaseModel):
    claim_id: str

@app.get("/")
def read_root():
    return {"message": "Insurance Claim API is running"}

@app.post("/claim/status")
def get_claim_status(data: ClaimRequest):
    claim = claims_db.get(data.claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim ID not found")
    return {"claim_id": data.claim_id, "status": claim["status"]}

# POST - Get claim date
@app.post("/claim/date")
def get_claim_date(data: ClaimRequest):
    claim = claims_db.get(data.claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim ID not found")
    return {"claim_id": data.claim_id, "claim_date": claim["claim_date"]}

# POST - Get latest comment
@app.post("/claim/comment")
def get_latest_comment(data: ClaimRequest):
    claim = claims_db.get(data.claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim ID not found")
    return {"claim_id": data.claim_id, "latest_comment": claim["latest_comment"]}
