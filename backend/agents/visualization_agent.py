import os
import logging
import pandas as pd
import numpy as np
from agents.base_agent import call_gemini_json, call_groq_json

logger = logging.getLogger("VisualizationAgent")
from utils.chart_generator import (
    generate_correlation_heatmap,
    generate_distribution_plot,
    generate_box_plot,
    generate_bar_chart,
    generate_scatter_plot,
    generate_missing_heatmap
)

GEMINI_MODEL = "gemini-2.0-flash-lite"
GROQ_MODEL = "llama-3.3-70b-versatile"

async def run_visualization_agent(df: pd.DataFrame, previous_context: dict) -> dict:
    """
    Asks GPT-OSS to decide which charts to generate based on columns metadata.
    Then programmatically creates those charts as base64 images and returns the specifications.
    """
    schema = previous_context.get("ingestion_agent", {}).get("schema", [])
    top_correlations = previous_context.get("eda_agent", {}).get("top_correlations", [])
    skewed_columns = previous_context.get("eda_agent", {}).get("skewed_columns", [])
    potential_target = previous_context.get("ingestion_agent", {}).get("potential_target", "")
    
    # 1. Gather column classification lists
    numeric_cols = []
    categorical_cols = []
    boolean_cols = []
    datetime_cols = []
    
    for item in schema:
        cname = item["column_name"]
        ctype = item["detected_type"]
        if ctype == "numeric":
            numeric_cols.append(cname)
        elif ctype == "categorical":
            categorical_cols.append(cname)
        elif ctype == "boolean":
            boolean_cols.append(cname)
        elif ctype == "datetime":
            datetime_cols.append(cname)

    # Ask the LLM to choose up to 6 of the most interesting plots to render
    system_prompt = (
        "You are an expert Visualization Agent. Your task is to select the most meaningful, "
        "revealing visualizations for a dataset based on its column names, data types, and correlations. "
        "Recommend specific columns to plot. Keep recommendations to at most 6 high-value charts, "
        "including distribution plots, scatter plots, box plots, and bar charts. "
        "Respond strictly in valid JSON format."
    )
    
    user_prompt = f"""
Dataset Column Types:
Numeric: {numeric_cols}
Categorical: {categorical_cols}
Boolean: {boolean_cols}
Datetime: {datetime_cols}

Top Correlated Columns:
{top_correlations}
Potential target variable: {potential_target}

Recommend up to 6 charts to generate. For each chart, specify:
1. "chart_type": "distribution" | "box" | "bar" | "scatter"
2. "x": "column_name"
3. "y": "column_name" (only for scatter or box)
4. "hue": "column_name" (optional, e.g. using the potential target column)
5. "title": "Brief descriptive title"

Return a JSON object containing:
{{
  "recommended_charts": [
     {{
       "chart_type": "distribution",
       "x": "age",
       "title": "Distribution of Age"
     }}
  ],
  "visual_theme_notes": "A brief comment on the chosen visualizations."
}}
"""
    
    # Get recommendation
    try:
        strategy = await call_gemini_json(GEMINI_MODEL, system_prompt, user_prompt)
    except Exception as e:
        logger.warning(f"Gemini API failed ({e}), falling back to Groq...")
        strategy = await call_groq_json(GROQ_MODEL, system_prompt, user_prompt)
    
    # Now, programmatically generate the charts based on the strategy + standard default charts
    charts_dict = {}
    
    # A. Always generate the missing heatmap (if missing data existed) and correlation heatmap
    try:
        charts_dict["correlation_heatmap"] = generate_correlation_heatmap(df)
    except Exception as e:
        pass
        
    try:
        # Generate missing values map using previous dataframe from ingestion if available
        # But we can also just run it on the current df, or before cleaning.
        # Since we only have the current df (which is cleaned), let's see.
        # We can draw it, it will just show empty if no nulls remain.
        charts_dict["missing_value_heatmap"] = generate_missing_heatmap(df)
    except Exception as e:
        pass

    # B. Generate recommended charts
    recommended_specs = strategy.get("recommended_charts", [])
    generated_count = 0
    
    for idx, spec in enumerate(recommended_specs):
        ctype = spec.get("chart_type")
        x = spec.get("x")
        y = spec.get("y")
        hue = spec.get("hue")
        title = spec.get("title", f"Chart {idx+1}")
        
        # Verify columns exist
        if x and x not in df.columns:
            continue
        if y and y not in df.columns:
            continue
        if hue and hue not in df.columns:
            hue = None
            
        chart_key = f"recommended_chart_{idx+1}"
        
        try:
            if ctype == "distribution":
                charts_dict[chart_key] = generate_distribution_plot(df, x)
                generated_count += 1
            elif ctype == "box":
                charts_dict[chart_key] = generate_box_plot(df, y, x)
                generated_count += 1
            elif ctype == "bar":
                charts_dict[chart_key] = generate_bar_chart(df, x)
                generated_count += 1
            elif ctype == "scatter" and y:
                charts_dict[chart_key] = generate_scatter_plot(df, x, y, hue)
                generated_count += 1
        except Exception as e:
            continue

    # C. Fallback: If no recommended charts were successfully generated, create simple distributions
    if generated_count == 0:
        for idx, col in enumerate(numeric_cols[:3]):
            try:
                charts_dict[f"recommended_chart_{idx+1}"] = generate_distribution_plot(df, col)
                generated_count += 1
            except:
                pass

    return {
        "charts": charts_dict,
        "specs": recommended_specs,
        "theme_notes": strategy.get("visual_theme_notes", "Charts successfully generated.")
    }
