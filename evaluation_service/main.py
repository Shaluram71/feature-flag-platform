from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from shared.hashing import compute_bucket
from shared.rules import evaluate_flag
from evaluation_service.repositories.flag_repository import InMemoryFlagRepository

flag_repository = InMemoryFlagRepository()

app = FastAPI(title="Feature Flag Evaluation Service")

class EvaluationRequest(BaseModel):
    flag_key: str
    user_id: str
    user_attributes: Dict[str, str]
    
class EvaluationResponse(BaseModel):
    flag_key: str
    variant: str
    value: Any
    version: int

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(req: EvaluationRequest):
    flag = flag_repository.get(req.flag_key)

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    bucket = compute_bucket(req.flag_key, req.user_id)

    try:
        variant = evaluate_flag(
            flag_version=flag,
            user_attributes=req.user_attributes,
            bucket=bucket,
        )
    except ValueError as e:
        # Misconfiguration = server error
        raise HTTPException(status_code=500, detail=str(e))

    return EvaluationResponse(
        flag_key=req.flag_key,
        variant=variant.name,
        value=variant.value,
        version=flag.version,
    )
