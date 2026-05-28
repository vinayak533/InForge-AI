import os
import io
import json
import pytest
import pandas as pd
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from utils.file_parser import parse_file
from utils.chart_generator import (
    generate_correlation_heatmap,
    generate_distribution_plot,
    generate_box_plot,
    generate_bar_chart,
    generate_scatter_plot,
    generate_missing_heatmap,
    generate_confusion_matrix_plot,
    generate_residual_plot,
    generate_feature_importance_plot
)
from utils.report_generator import generate_pdf_report
from agents.ingestion_agent import run_ingestion_agent
from agents.cleaning_agent import run_cleaning_agent
from agents.eda_agent import run_eda_agent
from agents.visualization_agent import run_visualization_agent
from agents.ml_agent import run_ml_agent
from agents.insights_agent import run_insights_agent
from agents.code_agent import run_code_agent
from agents.chat_agent import run_chat_agent
from pipeline.orchestrator import ConnectionManager, execute_pipeline, SESSIONS

# 1. Test utils/file_parser.py
def test_file_parser_csv():
    csv_data = b"col1,col2,col3\n1,foo,3.14\n2,bar,6.28"
    df = parse_file(csv_data, "test.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 3)
    assert list(df.columns) == ["col1", "col2", "col3"]

def test_file_parser_csv_latin1():
    csv_data = "col1,col2\n1,ééé\n2,ààà".encode("latin-1")
    df = parse_file(csv_data, "test.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert df.iloc[0, 1] == "ééé"

# 2. Test utils/chart_generator.py
def test_chart_generator_heatmap():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4],
        "b": [4, 3, 2, 1],
        "c": [2, 3, 1, 4]
    })
    b64_str = generate_correlation_heatmap(df)
    assert isinstance(b64_str, str)
    assert len(b64_str) > 0

def test_chart_generator_plots():
    df = pd.DataFrame({
        "num": [10, 20, 30, 40, 50],
        "cat": ["A", "B", "A", "B", "A"]
    })
    
    # Test distribution plot
    dist_img = generate_distribution_plot(df, "num")
    assert isinstance(dist_img, str)
    
    # Test box plot
    box_img = generate_box_plot(df, "num", "cat")
    assert isinstance(box_img, str)
    
    # Test bar chart
    bar_img = generate_bar_chart(df, "cat")
    assert isinstance(bar_img, str)
    
    # Test scatter plot
    scatter_img = generate_scatter_plot(df, "num", "num", "cat")
    assert isinstance(scatter_img, str)
    
    # Test missing map
    df_missing = df.copy()
    df_missing.iloc[0, 0] = np.nan
    miss_img = generate_missing_heatmap(df_missing)
    assert isinstance(miss_img, str)

def test_chart_generator_ml_plots():
    cm = np.array([[2, 0], [0, 2]])
    cm_img = generate_confusion_matrix_plot(cm, ["0", "1"])
    assert isinstance(cm_img, str)
    
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.1, 1.9, 3.05])
    res_img = generate_residual_plot(y_true, y_pred)
    assert isinstance(res_img, str)
    
    imp_img = generate_feature_importance_plot([0.5, 0.3, 0.2], ["x1", "x2", "x3"])
    assert isinstance(imp_img, str)

# 3. Test utils/report_generator.py (Dynamic colWidths validation)
def test_report_generator():
    context = {
        "row_count": 100,
        "column_count": 5,
        "potential_target": "target_col",
        "cleaning_agent": {
            "null_counts": {"total": 10},
            "duplicate_count": 2
        },
        "ml_agent": {
            "task_type": "regression",
            "best_model": "Ridge Regression",
            "best_score": 0.85,
            "model_results": [
                {"model": "Ridge Regression", "rmse": 0.1, "mae": 0.08, "r2_score": 0.85},
                {"model": "Linear Regression", "rmse": 0.11, "mae": 0.09, "r2_score": 0.83}
            ],
            "plots": {
                "residual_plot": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            }
        },
        "visualization_agent": {
            "charts": {
                "correlation_heatmap": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            }
        },
        "insights_agent": {
            "executive_summary": "Test Executive Summary",
            "insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Rec 1"]
        }
    }
    
    pdf_bytes = generate_pdf_report("test-session-id", context)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

# 4. Test Ingestion Agent
@pytest.mark.asyncio
@patch("agents.ingestion_agent.call_openrouter_json", new_callable=AsyncMock)
async def test_ingestion_agent(mock_call):
    mock_call.return_value = {
        "schema": [
            {"column_name": "feat1", "detected_type": "numeric", "reasoning": "numbers", "unique_count": 10, "missing_percent": 0.0},
            {"column_name": "feat2", "detected_type": "categorical", "reasoning": "strings", "unique_count": 2, "missing_percent": 0.0},
            {"column_name": "label", "detected_type": "categorical", "reasoning": "binary labels", "unique_count": 2, "missing_percent": 0.0}
        ],
        "potential_target": "label",
        "target_reasoning": "selected last column"
    }
    
    df = pd.DataFrame({
        "feat1": [1, 2, 3, 4],
        "feat2": ["yes", "no", "yes", "no"],
        "label": [1, 0, 1, 0]
    })
    
    res = await run_ingestion_agent(df)
    assert res["row_count"] == 4
    assert res["column_count"] == 3
    assert res["potential_target"] == "label"
    assert len(res["sample_rows"]) == 4

# 5. Test Cleaning Agent
@pytest.mark.asyncio
@patch("agents.cleaning_agent.call_openrouter_json", new_callable=AsyncMock)
async def test_cleaning_agent(mock_call):
    mock_call.return_value = {
        "imputations": {
            "feat1": "median"
        },
        "drop_duplicates": True,
        "drop_columns": [],
        "rationale": "clean details"
    }
    
    df = pd.DataFrame({
        "feat1": [1.0, np.nan, 3.0, 3.0],
        "feat2": ["yes", "no", "yes", "yes"]
    })
    
    schema_ctx = {
        "schema": [
            {"column_name": "feat1", "detected_type": "numeric"},
            {"column_name": "feat2", "detected_type": "categorical"}
        ]
    }
    
    res, cleaned_df = await run_cleaning_agent(df, schema_ctx)
    assert res["duplicate_count"] == 1
    assert cleaned_df.shape[0] == 3  # Duplicate dropped
    assert cleaned_df["feat1"].isnull().sum() == 0  # Imputed

# 6. Test EDA Agent
@pytest.mark.asyncio
@patch("agents.eda_agent.call_openrouter_json", new_callable=AsyncMock)
async def test_eda_agent(mock_call):
    mock_call.return_value = {
        "distribution_analysis": "Normal",
        "correlation_analysis": "None",
        "flags_analysis": "None"
    }
    
    df = pd.DataFrame({
        "feat1": [1.0, 2.0, 3.0, 4.0],
        "feat2": [2.0, 4.0, 6.0, 8.0]
    })
    
    res = await run_eda_agent(df, {})
    assert "descriptive_stats" in res
    assert "top_correlations" in res
    assert len(res["top_correlations"]) > 0
    assert res["top_correlations"][0]["feature_1"] == "feat1"
    assert res["top_correlations"][0]["feature_2"] == "feat2"

# 7. Test Visualization Agent
@pytest.mark.asyncio
@patch("agents.visualization_agent.call_gemini_json", new_callable=AsyncMock)
async def test_visualization_agent(mock_call):
    mock_call.return_value = {
        "recommended_charts": [
            {"chart_type": "distribution", "x": "feat1", "title": "Feat1 Dist"},
            {"chart_type": "scatter", "x": "feat1", "y": "feat2", "title": "Scatter"}
        ],
        "visual_theme_notes": "Sleek look"
    }
    
    df = pd.DataFrame({
        "feat1": [1.0, 2.0, 3.0, 4.0],
        "feat2": [2.0, 4.0, 6.0, 8.0]
    })
    
    prev_ctx = {
        "ingestion_agent": {
            "schema": [
                {"column_name": "feat1", "detected_type": "numeric"},
                {"column_name": "feat2", "detected_type": "numeric"}
            ],
            "potential_target": "feat2"
        },
        "eda_agent": {
            "top_correlations": [{"feature_1": "feat1", "feature_2": "feat2", "correlation": 1.0}]
        }
    }
    
    res = await run_visualization_agent(df, prev_ctx)
    assert "charts" in res
    assert "correlation_heatmap" in res["charts"]
    assert "recommended_chart_1" in res["charts"]
    assert "recommended_chart_2" in res["charts"]

# 8. Test Machine Learning Agent (Classification & Regression & Clustering)
@pytest.mark.asyncio
@patch("agents.ml_agent.call_groq_json", new_callable=AsyncMock)
async def test_ml_agent_classification(mock_call):
    mock_call.return_value = {
        "model_rationalization": "LogReg performed well.",
        "feature_influence_explanation": "Feat1 was key.",
        "performance_verdict": "Production ready."
    }
    
    df = pd.DataFrame({
        "feat1": [1.0, 2.0, 1.5, 3.0, 2.2, 1.8, 3.5, 1.2, 2.8, 3.1],
        "feat2": [0.5, 1.5, 1.0, 2.0, 1.8, 0.9, 2.2, 0.4, 1.6, 2.5],
        "label": [0, 1, 0, 1, 1, 0, 1, 0, 1, 1]
    })
    
    prev_ctx = {
        "ingestion_agent": {
            "potential_target": "label"
        }
    }
    
    res = await run_ml_agent(df, prev_ctx)
    assert res["task_type"] == "classification"
    assert len(res["model_results"]) > 0
    assert "confusion_matrix" in res["plots"]
    assert "feature_importance" in res["plots"]

@pytest.mark.asyncio
@patch("agents.ml_agent.call_groq_json", new_callable=AsyncMock)
async def test_ml_agent_regression(mock_call):
    mock_call.return_value = {
        "model_rationalization": "Ridge Regression was best.",
        "feature_influence_explanation": "Feat1 was main driver.",
        "performance_verdict": "Production ready."
    }
    
    df = pd.DataFrame({
        "feat1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "feat2": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5],
        "label": [1.5, 3.5, 5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5]
    })
    
    prev_ctx = {
        "ingestion_agent": {
            "potential_target": "label"
        }
    }
    
    res = await run_ml_agent(df, prev_ctx)
    assert res["task_type"] == "regression"
    assert len(res["model_results"]) > 0
    assert "residual_plot" in res["plots"]

@pytest.mark.asyncio
@patch("agents.ml_agent.call_groq_json", new_callable=AsyncMock)
async def test_ml_agent_clustering(mock_call):
    mock_call.return_value = {
        "model_rationalization": "KMeans was selected.",
        "feature_influence_explanation": "Variance based influence.",
        "performance_verdict": "Use for customer profiling."
    }
    
    df = pd.DataFrame({
        "feat1": [1.0, 2.0, 3.0, 1.1, 2.1, 3.1, 1.05, 2.05, 3.05, 1.2],
        "feat2": [0.5, 1.5, 2.5, 0.6, 1.6, 2.6, 0.55, 1.55, 2.55, 0.4]
    })
    
    prev_ctx = {
        "ingestion_agent": {
            "potential_target": "None"
        }
    }
    
    res = await run_ml_agent(df, prev_ctx)
    assert res["task_type"] == "clustering"
    assert len(res["model_results"]) > 0
    assert "feature_importance" in res["plots"]

# 9. Test Insights and Code & Chat Agents
@pytest.mark.asyncio
@patch("agents.insights_agent.call_groq_json", new_callable=AsyncMock)
async def test_insights_agent(mock_call):
    mock_call.return_value = {
        "executive_summary": "All clear.",
        "insights": ["Highly related correlations"],
        "recommendations": ["Rec action"],
        "data_quality_flags": ["No flags"]
    }
    
    res = await run_insights_agent({})
    assert res["executive_summary"] == "All clear."

@pytest.mark.asyncio
@patch("agents.code_agent.call_groq", new_callable=AsyncMock)
async def test_code_agent(mock_call):
    mock_call.return_value = "import pandas as pd\nprint('hello')"
    
    res = await run_code_agent({})
    assert "import pandas as pd" in res

@pytest.mark.asyncio
@patch("agents.chat_agent.call_groq", new_callable=AsyncMock)
async def test_chat_agent(mock_call):
    mock_call.return_value = "The correlations show feature 1 is very strong."
    
    res = await run_chat_agent("What are the correlations?", [], {})
    assert "correlations" in res

# 10. Test Connection Manager & Pipeline Orchestrator
@pytest.mark.asyncio
async def test_connection_manager():
    manager = ConnectionManager()
    
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_json = AsyncMock()
    
    # Test connection
    await manager.connect("session-123", mock_ws)
    assert "session-123" in manager.active_connections
    assert mock_ws in manager.active_connections["session-123"]
    
    # Test send update
    await manager.send_status_update("session-123", 0, "ingestion", "Label", "Text", "active")
    mock_ws.send_json.assert_called()
    
    # Test disconnect
    manager.disconnect("session-123", mock_ws)
    assert "session-123" not in manager.active_connections

@pytest.mark.asyncio
@patch("pipeline.orchestrator.run_ingestion_agent", new_callable=AsyncMock)
@patch("pipeline.orchestrator.run_cleaning_agent", new_callable=AsyncMock)
@patch("pipeline.orchestrator.run_eda_agent", new_callable=AsyncMock)
@patch("pipeline.orchestrator.run_visualization_agent", new_callable=AsyncMock)
@patch("pipeline.orchestrator.run_ml_agent", new_callable=AsyncMock)
@patch("pipeline.orchestrator.run_insights_agent", new_callable=AsyncMock)
@patch("pipeline.orchestrator.run_code_agent", new_callable=AsyncMock)
async def test_execute_pipeline(
    mock_code, mock_insights, mock_ml, mock_vis, mock_eda, mock_clean, mock_ingestion
):
    mock_ingestion.return_value = {
        "schema": [{"column_name": "col1", "detected_type": "numeric"}],
        "potential_target": "col1",
        "target_reasoning": "selected last",
        "row_count": 4,
        "column_count": 1,
        "sample_rows": []
    }
    
    mock_clean.return_value = (
        {
            "null_counts": {"total": 0},
            "duplicate_count": 0,
            "outlier_columns": [],
            "outlier_counts": {},
            "cleaning_log": [],
            "cleaned_shape": [4, 1],
            "rationale": "clean"
        },
        pd.DataFrame({"col1": [1, 2, 3, 4]})
    )
    
    mock_eda.return_value = {
        "descriptive_stats": {},
        "categorical_counts": {},
        "correlation_matrix": {},
        "top_correlations": [],
        "skewed_columns": [],
        "zero_variance_columns": [],
        "textual_insights": {}
    }
    
    mock_vis.return_value = {"charts": {}, "specs": [], "theme_notes": "notes"}
    
    mock_ml.return_value = {
        "task_type": "clustering",
        "model_results": [],
        "best_model": "KMeans",
        "best_score": 0.5,
        "plots": {},
        "explanation": {}
    }
    
    mock_insights.return_value = {
        "executive_summary": "summary",
        "insights": [],
        "recommendations": [],
        "data_quality_flags": []
    }
    
    mock_code.return_value = "code script"
    
    csv_bytes = b"col1\n1\n2\n3\n4"
    await execute_pipeline("session-999", csv_bytes, "test.csv")
    
    assert "session-999" in SESSIONS
    assert SESSIONS["session-999"]["completed"] is True
    assert SESSIONS["session-999"]["context"]["code_agent"]["code"] == "code script"
