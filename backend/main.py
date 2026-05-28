import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
import io
import math
import numpy as np

from pipeline.orchestrator import execute_pipeline, SESSIONS, ws_manager
from utils.report_generator import generate_pdf_report
from agents.chat_agent import run_chat_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InForgeMain")

app = FastAPI(title="InForge AI API", description="Autonomous multi-agent data analytics engine")

# Configure CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chat history in-memory database
# Stores: {session_id: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
CHAT_HISTORIES = {}

class ChatMessage(BaseModel):
    message: str

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Accepts CSV or Excel files, generates a session ID,
    and runs the analytical pipeline in a background task.
    """
    filename = file.filename
    if not filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported.")
        
    try:
        file_content = await file.read()
        session_id = str(uuid.uuid4())
        
        # Start pipeline orchestrator in the background
        background_tasks.add_task(execute_pipeline, session_id, file_content, filename)
        
        return {
            "session_id": session_id,
            "filename": filename,
            "status": "processing"
        }
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time agent pipeline progress updates.
    """
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            # We don't expect incoming messages from client, but keeping connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
        ws_manager.disconnect(session_id, websocket)

def sanitize_nan(data, seen=None):
    """
    Recursively replaces NaN, Inf, and -Inf values in a dictionary/list with None.
    Also converts numpy types to standard python types and handles circular references.
    """
    if seen is None:
        seen = set()
        
    # Prevent circular references
    if id(data) in seen:
        return None
    
    if isinstance(data, (dict, list)):
        seen.add(id(data))

    if isinstance(data, dict):
        return {str(k): sanitize_nan(v, seen) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_nan(x, seen) for x in data]
    elif isinstance(data, (float, int)):
        if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
            return None
        return data
    elif isinstance(data, np.generic):
        val = data.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
        return val
    elif isinstance(data, np.ndarray):
        return sanitize_nan(data.tolist(), seen)
    elif str(data) in ('NaN', 'nan', 'NaT', 'inf', '-inf'):
        return None
    else:
        try:
            # Check for numpy NaN values that aren't np.generic but act like float
            if hasattr(data, '__float__'):
                fval = float(data)
                if math.isnan(fval) or math.isinf(fval):
                    return None
                return fval
        except (ValueError, TypeError):
            pass
        return str(data) if not isinstance(data, (bool, type(None))) else data

@app.get("/results/{session_id}")
async def get_results(session_id: str):
    """
    Returns the compiled multi-agent analysis context JSON.
    """
    logger.info(f"Fetching results for session {session_id}")
    if session_id not in SESSIONS:
        logger.warning(f"Session {session_id} not found.")
        raise HTTPException(status_code=404, detail="Session not found.")
        
    session = SESSIONS[session_id]
    if not session.get("completed", False):
        if "error" in session:
            logger.error(f"Session {session_id} failed with error: {session['error']}")
            return {"status": "failed", "error": session["error"]}
        logger.info(f"Session {session_id} is still processing.")
        return {"status": "processing"}
        
    try:
        logger.info(f"Serializing results for session {session_id}...")
        sanitized = sanitize_nan(session["context"])
        logger.info(f"Successfully sanitized results for session {session_id}")
        return {
            "status": "completed",
            "results": sanitized
        }
    except Exception as e:
        logger.exception(f"Failed to serialize results for session {session_id}")
        raise HTTPException(status_code=500, detail=f"Internal error during result serialization: {str(e)}")

@app.post("/chat/{session_id}")
async def chat_message(session_id: str, payload: ChatMessage):
    """
    Handles floating chatbot conversational queries regarding the dataset findings.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    session = SESSIONS[session_id]
    if not session.get("completed", False):
        raise HTTPException(status_code=400, detail="Analysis is still in progress.")
        
    user_query = payload.message
    
    # Initialize history if empty
    if session_id not in CHAT_HISTORIES:
        CHAT_HISTORIES[session_id] = []
        
    history = CHAT_HISTORIES[session_id]
    
    try:
        # Call chat agent
        response_text = await run_chat_agent(user_query, history, session["context"])
        
        # Save to history
        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": response_text})
        
        return {
            "answer": response_text,
            "history": history
        }
    except Exception as e:
        logger.exception("Chatbot query failed")
        raise HTTPException(status_code=500, detail=f"Chatbot failed to formulate a response: {str(e)}")

@app.get("/export/csv/{session_id}")
async def export_csv(session_id: str):
    """
    Downloads the fully cleaned post-cleaning dataset as a CSV file.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    session = SESSIONS[session_id]
    cleaned_df = session.get("cleaned_df")
    if cleaned_df is None:
        raise HTTPException(status_code=400, detail="Cleaned dataset not available.")
        
    stream = io.StringIO()
    cleaned_df.to_csv(stream, index=False)
    
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=cleaned_{session['raw_filename']}"
    return response

@app.get("/export/pdf/{session_id}")
async def export_pdf(session_id: str):
    """
    Downloads a beautifully formatted PDF analytical report.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    session = SESSIONS[session_id]
    if not session.get("completed", False):
        raise HTTPException(status_code=400, detail="Analysis is still in progress.")
        
    try:
        pdf_bytes = generate_pdf_report(session_id, session["context"])
        
        response = Response(content=pdf_bytes, media_type="application/pdf")
        response.headers["Content-Disposition"] = f"attachment; filename=InForge_Report_{session_id[:8]}.pdf"
        return response
    except Exception as e:
        logger.exception("PDF compiling failed")
        raise HTTPException(status_code=500, detail=f"Failed to compile PDF report: {str(e)}")

# Mount frontend static files if they exist
frontend_dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/dist")
if os.path.exists(frontend_dist_path):
    logger.info(f"Mounting static files from {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="static")
else:
    local_dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    if os.path.exists(local_dist_path):
        logger.info(f"Mounting static files from {local_dist_path}")
        app.mount("/", StaticFiles(directory=local_dist_path, html=True), name="static")
    else:
        logger.warning("No static files directory found (expected ../frontend/dist or ./dist)")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("ENV") == "dev"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
