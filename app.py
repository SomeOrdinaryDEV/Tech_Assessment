import os
import base64
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core.pipeline import MedtronicsCorePipeline
from portal.teleconsult import teleconsult_portal
from engines.safety.telemetry import telemetry_tracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("medtronics_app")

app = FastAPI(title="Medtronics_Project", description="Voice-First Healthcare & Government Scheme Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = MedtronicsCorePipeline()

# Static files directory setup
static_dir = os.path.join(settings.BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Medtronics_Project Voice Mini-App Backend is Running.</h1>"

@app.get("/clinician", response_class=HTMLResponse)
async def serve_clinician_portal():
    portal_file = os.path.join(static_dir, "clinician.html")
    if os.path.exists(portal_file):
        with open(portal_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Clinician Portal Backend is Running.</h1>"

@app.post("/api/process-audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        response = await pipeline.process_voice_input(audio_bytes)
        return response.dict()
    except Exception as e:
        logger.error(f"Error processing audio endpoint: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/process-text")
async def process_text(text: str = Form(...), session_id: str = Form(None)):
    try:
        # Mock STT pass for direct text testing
        from core.models import STTResult
        stt_result = STTResult(transcript=text, language="hi-IN", confidence=1.0)
        
        # Evaluate safety
        safety_eval = pipeline.safety_gate.evaluate_safety(text)
        if safety_eval.is_emergency:
            return (await pipeline._handle_emergency_escalation(session_id or "txt-1", stt_result, safety_eval, 0)).dict()
            
        intent_result = pipeline.intent_classifier.classify_intent(text)
        if intent_result.domain == "out_of_scope":
            rejection_text = "Main srif dawaiyan, sarkari yojana, aspatal, aur swasthya jaanch me madad kar sakta hoon."
            audio_b64 = await pipeline.tts_engine.synthesize_speech(rejection_text, "hi-IN")
            return {
                "session_id": session_id or "txt-1",
                "transcript": text,
                "language": "hi-IN",
                "domain": "out_of_scope",
                "text_response": rejection_text,
                "audio_b64": audio_b64,
                "is_rejection": True
            }

        rag_context = pipeline.rag_manager.query_isolated_domain(intent_result.domain, text)
        response_text = pipeline.synthesizer.synthesize_response(rag_context, "hi-IN")
        audio_b64 = await pipeline.tts_engine.synthesize_speech(response_text, "hi-IN")

        return {
            "session_id": session_id or "txt-1",
            "transcript": text,
            "language": "hi-IN",
            "domain": intent_result.domain,
            "text_response": response_text,
            "audio_b64": audio_b64,
            "is_emergency": False,
            "is_rejection": False
        }
    except Exception as e:
        logger.error(f"Error processing text endpoint: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("Voice WebSocket connection established.")
    try:
        while True:
            data = await websocket.receive_bytes()
            response = await pipeline.process_voice_input(data)
            await websocket.send_json(response.dict())
    except WebSocketDisconnect:
        logger.info("Voice WebSocket disconnected.")

@app.websocket("/ws/clinician")
async def clinician_websocket(websocket: WebSocket):
    await teleconsult_portal.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        teleconsult_portal.disconnect(websocket)

@app.get("/api/telemetry")
async def get_telemetry():
    return telemetry_tracker.get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
