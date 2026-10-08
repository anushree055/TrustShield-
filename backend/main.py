from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path

from services.url_analyzer import analyze_url
from services.message_analyzer import analyze_message
from services.ocr_service import extract_text
from services.recovery_assistant import build_recovery_plan
from database import init_db, save_analysis, list_history, get_history_item, delete_item, clear_history, stats, save_recovery_use

app = FastAPI(title="TrustShield API", version="1.0.0", description="Explainable scam detection and risk analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2048)

class MessageRequest(BaseModel):
    text: str = Field(min_length=2, max_length=20000)

class FullRequest(BaseModel):
    url: str | None = None
    text: str | None = None

class RecoveryRequest(BaseModel):
    # ID of the original analysis this recovery is linked to (optional)
    analysis_id: int | None = None
    # Original analysis metadata — used to personalise advice
    scam_type: str = "Unknown"
    risk_score: int = 50
    signals: list[str] = []
    # What the user selected they did
    interactions: list[str]
    # Answers to optional follow-up questions
    follow_ups: dict = {}

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TrustShield", "version": "1.0.0"}

@app.post("/api/analyze/url")
def url_analysis(body: URLRequest):
    result = analyze_url(body.url)
    result["analysis_id"] = save_analysis("URL", body.url, result)
    return result

@app.post("/api/analyze/message")
def message_analysis(body: MessageRequest):
    result = analyze_message(body.text)
    result["analysis_id"] = save_analysis("Message", body.text, result)
    return result

@app.post("/api/analyze/full")
def full_analysis(body: FullRequest):
    if not (body.url or body.text):
        raise HTTPException(400, "Provide a URL, message, or both.")
    pieces = []
    if body.url:
        pieces.append(analyze_url(body.url))
    if body.text:
        pieces.append(analyze_message(body.text))
    best = max(pieces, key=lambda x: x["risk_score"])
    combined = dict(best)
    if len(pieces) == 2:
        combined["risk_score"] = min(100, int(round(pieces[0]["risk_score"] * 0.45 + pieces[1]["risk_score"] * 0.55)))
        if combined["risk_score"] <= 20: combined["risk_level"] = "Very Low Risk"
        elif combined["risk_score"] <= 40: combined["risk_level"] = "Low Risk"
        elif combined["risk_score"] <= 60: combined["risk_level"] = "Moderate Risk"
        elif combined["risk_score"] <= 80: combined["risk_level"] = "High Risk"
        else: combined["risk_level"] = "Very High Risk"
        combined["explanation"] = "Combined URL and message analysis. " + combined["explanation"]
        combined["detected_signals"] = list(dict.fromkeys(pieces[0]["detected_signals"] + pieces[1]["detected_signals"]))
    preview = " | ".join(x for x in [body.url, body.text] if x)
    combined["analysis_id"] = save_analysis("Full Analysis", preview, combined)
    return combined

@app.post("/api/analyze/screenshot")
async def screenshot_analysis(file: UploadFile = File(...)):
    allowed = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Upload a PNG, JPG, JPEG, or WEBP image.")
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(400, "Image must be smaller than 8 MB.")
    ocr = extract_text(data)
    if not ocr.get("success") or len(ocr.get("text", "")) < 8:
        return {
            "ocr_text": ocr.get("text", ""),
            "ocr_success": False,
            "message": "We could not extract enough readable text. Try a clearer screenshot or edit/paste the text manually."
        }
    result = analyze_message(ocr["text"])
    result["ocr_text"] = ocr["text"]
    result["ocr_success"] = True
    result["analysis_id"] = save_analysis("Screenshot", ocr["text"], result)
    return result

@app.get("/api/history")
def history(limit: int = 100):
    return list_history(limit)

@app.get("/api/history/{item_id}")
def history_item(item_id: int):
    item = get_history_item(item_id)
    if not item:
        raise HTTPException(404, "Analysis not found")
    return item

@app.delete("/api/history/{item_id}")
def remove_history(item_id: int):
    return {"deleted": delete_item(item_id)}

@app.delete("/api/history")
def remove_all_history():
    clear_history()
    return {"deleted": True}

@app.get("/api/stats")
def get_stats():
    return stats()

@app.post("/api/recovery")
def recovery(body: RecoveryRequest):
    """
    Accept what the user already did with suspicious content and return a
    personalised, prioritised recovery plan.

    The plan is entirely rule-based — no ML, no random output.
    """
    plan = build_recovery_plan(
        interactions=body.interactions,
        follow_ups=body.follow_ups,
        scam_type=body.scam_type,
        risk_score=body.risk_score,
        signals=body.signals,
    )
    # Optionally persist that the recovery assistant was used (no sensitive data)
    if body.analysis_id:
        save_recovery_use(
            analysis_id=body.analysis_id,
            severity=plan["severity"],
            interactions=body.interactions,
        )
    return plan
