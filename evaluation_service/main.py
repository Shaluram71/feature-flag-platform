from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import time
from shared.hashing import compute_bucket
from shared.rules import evaluate_flag
from shared.models import FlagVersion, Variant, TargetingRule

FLAG_STORE : dict[str, FlagVersion]
FLAG_STORE = {
    "new_checkout": FlagVersion(
        flag_key="new_checkout",
        version=1,
        enabled=True,
        rules=[
            TargetingRule(
                attribute="country",
                operator="equals",
                value="US",
                variants=[
                    Variant(name="on", value=True, weight=50),
                    Variant(name="off", value=False, weight=50),
                ],
            )
        ],
        default_variant=Variant(name="off", value=False, weight=100),
        created_at= "2026-01-21T00:36:00Z",
    )
}

app = FastAPI(title="Feature Flag Evaluation Service")

class EvaluationRequest(BaseModel):
    flag_version: str
    user_id: str
    user_attributes: Dict[str, str]
    
class EvaluationResponse(BaseModel):
    flag_key: str
    variant: str
    value: Any
    version: int

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(req: EvaluationRequest):
    flag = FLAG_STORE.get(req.flag_key)

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    bucket = compute_bucket(req.flag_key, req.user_id)

    try:
        variant = evaluate_flag(
            flag_version=flag,
            user_attributes=req.attributes,
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
