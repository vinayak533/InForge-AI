import logging
import asyncio
import pandas as pd
from utils.file_parser import parse_file
from agents.ingestion_agent import run_ingestion_agent
from agents.cleaning_agent import run_cleaning_agent
from agents.eda_agent import run_eda_agent
from agents.visualization_agent import run_visualization_agent
from agents.ml_agent import run_ml_agent
from agents.insights_agent import run_insights_agent
from agents.code_agent import run_code_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PipelineOrchestrator")

# Global session database in memory
# Stores: {session_id: {"context": {...}, "df": pd.DataFrame, "cleaned_df": pd.DataFrame, "raw_filename": str}}
SESSIONS = {}

class ConnectionManager:
    """
    Manages active WebSocket connections to stream pipeline progress.
    """
    def __init__(self):
        self.active_connections: dict[str, list] = {}

    async def connect(self, session_id: str, websocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Replay progress history if it exists for this session
        if session_id in SESSIONS and "progress_history" in SESSIONS[session_id]:
            for message in SESSIONS[session_id]["progress_history"]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to replay status to WebSocket: {str(e)}")

    def disconnect(self, session_id: str, websocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected for session {session_id}")

    async def send_status_update(self, session_id: str, step_index: int, agent_name: str, label: str, status_text: str, state: str):
        """
        Sends a progress update to all active websockets for a session.
        state: 'pending' | 'active' | 'completed' | 'failed'
        """
        message = {
            "step_index": step_index,
            "agent_name": agent_name,
            "label": label,
            "status_text": status_text,
            "state": state
        }
        
        # Save to session progress history for future WebSocket connections
        if session_id in SESSIONS:
            if "progress_history" not in SESSIONS[session_id]:
                SESSIONS[session_id]["progress_history"] = []
            SESSIONS[session_id]["progress_history"].append(message)
            
        if session_id not in self.active_connections:
            return
        
        # Broadcast
        dead_sockets = []
        for ws in self.active_connections[session_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.append(ws)
                
        for ws in dead_sockets:
            self.disconnect(session_id, ws)

ws_manager = ConnectionManager()

# Define pipeline steps
STEPS = [
    {"name": "ingestion", "label": "Data Ingestion"},
    {"name": "cleaning", "label": "Data Cleaning"},
    {"name": "eda", "label": "Exploration"},
    {"name": "visualization", "label": "Visualization"},
    {"name": "ml", "label": "Machine Learning"},
    {"name": "insights", "label": "Insights"},
    {"name": "code", "label": "Code Generation"},
    {"name": "finalizing", "label": "Finalizing"}
]

async def execute_pipeline(session_id: str, file_content: bytes, filename: str):
    """
    Runs the sequential 8-step agent pipeline, passing context
    and streaming real-time status updates.
    """
    logger.info(f"Starting pipeline for session {session_id} with file {filename}")
    
    # Initialize session database entry
    SESSIONS[session_id] = {
        "raw_filename": filename,
        "context": {
            "session_id": session_id,
            "filename": filename,
        },
        "df": None,
        "cleaned_df": None,
        "completed": False,
        "progress_history": []
    }
    
    try:
        # STEP 0: Parse the uploaded file
        await ws_manager.send_status_update(session_id, 0, "ingestion", "Data Ingestion", f"Parsing file '{filename}'...", "active")
        df = parse_file(file_content, filename)
        SESSIONS[session_id]["df"] = df
        
        row_cnt = len(df)
        col_cnt = len(df.columns)
        
        # STEP 1: Ingestion Agent
        await ws_manager.send_status_update(session_id, 0, "ingestion", "Data Ingestion", f"Scanning {row_cnt:,} rows across {col_cnt:,} columns...", "active")
        ingestion_results = await run_ingestion_agent(df)
        SESSIONS[session_id]["context"]["ingestion_agent"] = ingestion_results
        SESSIONS[session_id]["context"]["row_count"] = ingestion_results["row_count"]
        SESSIONS[session_id]["context"]["column_count"] = ingestion_results["column_count"]
        SESSIONS[session_id]["context"]["potential_target"] = ingestion_results["potential_target"]
        SESSIONS[session_id]["context"]["sample_rows"] = ingestion_results["sample_rows"]
        await ws_manager.send_status_update(session_id, 0, "ingestion", "Data Ingestion", f"Successfully analyzed schema for {col_cnt} columns.", "completed")
        
        # STEP 2: Cleaning Agent
        await ws_manager.send_status_update(session_id, 1, "cleaning", "Data Cleaning", "Assessing data quality issues...", "active")
        # Add small artificial delay so the UI animation looks elegant and readable
        await asyncio.sleep(1.0)
        
        cleaning_results, cleaned_df = await run_cleaning_agent(df, ingestion_results)
        SESSIONS[session_id]["cleaned_df"] = cleaned_df
        SESSIONS[session_id]["context"]["cleaning_agent"] = cleaning_results
        
        nulls_found = cleaning_results["null_counts"]["total"]
        dups_found = cleaning_results["duplicate_count"]
        await ws_manager.send_status_update(session_id, 1, "cleaning", "Data Cleaning", f"Found {nulls_found} missing values and {dups_found} duplicates. Imputing and fixing...", "active")
        await asyncio.sleep(1.2)
        
        await ws_manager.send_status_update(session_id, 1, "cleaning", "Data Cleaning", f"Cleaned dataset. Shape is now {cleaned_df.shape[0]}x{cleaned_df.shape[1]}.", "completed")
        
        # STEP 3: EDA Agent
        await ws_manager.send_status_update(session_id, 2, "eda", "Exploration", f"Analyzing distributions and correlations across {cleaned_df.shape[1]} features...", "active")
        await asyncio.sleep(1.0)
        
        eda_results = await run_eda_agent(cleaned_df, SESSIONS[session_id]["context"])
        SESSIONS[session_id]["context"]["eda_agent"] = eda_results
        await ws_manager.send_status_update(session_id, 2, "eda", "Exploration", "Successfully computed correlations and descriptive metrics.", "completed")
        
        # STEP 4: Visualization Agent
        chart_count = 2 + len(eda_results.get("top_correlations", []))
        await ws_manager.send_status_update(session_id, 3, "visualization", "Visualization", f"Generating {chart_count} custom dark-themed visualizations...", "active")
        await asyncio.sleep(1.0)
        
        vis_results = await run_visualization_agent(cleaned_df, SESSIONS[session_id]["context"])
        SESSIONS[session_id]["context"]["visualization_agent"] = vis_results
        await ws_manager.send_status_update(session_id, 3, "visualization", "Visualization", f"Rendered heatmap and {len(vis_results.get('specs', []))} plots.", "completed")
        
        # STEP 5: Machine Learning Agent
        task_label = "predictive modeling"
        await ws_manager.send_status_update(session_id, 4, "ml", "Machine Learning", f"Auto-detecting task. Training and comparing 4 ML models...", "active")
        await asyncio.sleep(1.0)
        
        ml_results = await run_ml_agent(cleaned_df, SESSIONS[session_id]["context"])
        SESSIONS[session_id]["context"]["ml_agent"] = ml_results
        best_mod = ml_results["best_model"]
        best_sc = ml_results["best_score"]
        
        score_text = f"{best_sc:.3f}" if isinstance(best_sc, (int, float)) else str(best_sc)
        await ws_manager.send_status_update(session_id, 4, "ml", "Machine Learning", f"Identified best model: {best_mod} (Score: {score_text}). Running explanations...", "active")
        await asyncio.sleep(1.2)
        await ws_manager.send_status_update(session_id, 4, "ml", "Machine Learning", "Trained models successfully. SHAP-equivalent feature importance saved.", "completed")
        
        # STEP 6: Insights Agent
        await ws_manager.send_status_update(session_id, 5, "insights", "Insights", "Synthesizing findings into business insights...", "active")
        await asyncio.sleep(1.0)
        
        insights_results = await run_insights_agent(SESSIONS[session_id]["context"])
        SESSIONS[session_id]["context"]["insights_agent"] = insights_results
        await ws_manager.send_status_update(session_id, 5, "insights", "Insights", f"Synthesized executive summary and {len(insights_results.get('insights', []))} insights.", "completed")
        
        # STEP 7: Code Generation Agent
        await ws_manager.send_status_update(session_id, 6, "code", "Code Generation", "Writing complete analysis code...", "active")
        await asyncio.sleep(1.0)
        
        code_results = await run_code_agent(SESSIONS[session_id]["context"])
        SESSIONS[session_id]["context"]["code_agent"] = {"code": code_results}
        await ws_manager.send_status_update(session_id, 6, "code", "Code Generation", "Complete Python analysis script generated.", "completed")
        
        # STEP 8: Finalizing
        await ws_manager.send_status_update(session_id, 7, "finalizing", "Finalizing", "Analysis complete! Loading dashboard...", "active")
        await asyncio.sleep(0.8)
        
        SESSIONS[session_id]["completed"] = True
        await ws_manager.send_status_update(session_id, 7, "finalizing", "Finalizing", "System ready.", "completed")
        logger.info(f"Pipeline executed successfully for session {session_id}")
        
    except Exception as e:
        logger.exception(f"Pipeline failed for session {session_id}")
        # Stream failure details to user
        await ws_manager.send_status_update(session_id, 0, "ingestion", "Error", f"Pipeline failed: {str(e)}", "failed")
        SESSIONS[session_id]["error"] = str(e)
