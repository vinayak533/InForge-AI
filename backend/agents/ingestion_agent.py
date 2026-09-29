import os
import logging
import pandas as pd
import numpy as np
from agents.base_agent import call_openrouter_json

logger = logging.getLogger("IngestionAgent")
MODEL = "meta-llama/llama-3.3-70b-instruct"

async def run_ingestion_agent(df: pd.DataFrame) -> dict:
    """
    Parses structural parameters of the DataFrame and invokes LLM
    to analyze target features and build column schema.
    """
    row_count = len(df)
    col_count = len(df.columns)
    logger.info(f"Ingestion agent processing {row_count} rows and {col_count} columns.")
    
    # Collect basic column information
    columns_info = []
    for col in df.columns:
        try:
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())
            dtype = str(df[col].dtype)
            
            # Get sample values (first 3 unique or non-null values)
            sample_vals = df[col].dropna().head(3).tolist()
            sample_vals_str = [str(x) for x in sample_vals]
            
            # Heuristics for typing
            is_bool = unique_count == 2 and set(df[col].dropna().unique()).issubset({0, 1, True, False, '0', '1', 'Y', 'N', 'Yes', 'No'})
            
            columns_info.append({
                "name": str(col),
                "pandas_type": dtype,
                "unique_values_count": unique_count,
                "missing_values_count": null_count,
                "samples": sample_vals_str,
                "is_bool": is_bool
            })
        except Exception as e:
            logger.warning(f"Failed to analyze column '{col}': {e}")
            continue

    # Prepare user prompt for LLM
    system_prompt = (
        "You are an expert Data Ingestion Agent. Your role is to examine structural column metadata, "
        "detect their biological/business data types (e.g. numeric, categorical, datetime, boolean, ID, text), "
        "and determine the most likely 'potential_target' column for modeling (usually the last column, "
        "or a low-cardinality label column, unless it's a clear ID or unique key). "
        "Respond strictly in valid JSON format."
    )
    
    user_prompt = f"""
Analyze this dataset structure and classify each column:
Total Rows: {row_count}
Total Columns: {col_count}
Columns Details:
{columns_info}

Return a JSON object containing:
{{
  "schema": [
     {{
       "column_name": "name of column",
       "detected_type": "numeric | categorical | datetime | boolean | text | id",
       "reasoning": "why it was classified this way",
       "unique_count": N,
       "missing_percent": Float
     }}
  ],
  "potential_target": "column_name_here",
  "target_reasoning": "why this column is selected as the predictive modeling target"
}}
"""
    
    fallback_schema = []
    for info in columns_info:
        unique_count = info["unique_values_count"]
        missing_percent = round((info["missing_values_count"] / row_count) * 100, 2) if row_count else 0.0
        dtype = info["pandas_type"]
        name = info["name"]
        lower_name = name.lower()

        if unique_count == row_count and row_count > 0:
            detected_type = "id"
            reasoning = "Column has unique values for every row."
        elif info["is_bool"]:
            detected_type = "boolean"
            reasoning = "Column has two boolean-like values."
        elif "datetime" in dtype or "date" in lower_name or "time" in lower_name:
            detected_type = "datetime"
            reasoning = "Column name or dtype indicates date/time data."
        elif pd.api.types.is_numeric_dtype(df[name]):
            detected_type = "numeric"
            reasoning = "Column is numeric."
        elif unique_count <= max(20, row_count * 0.2):
            detected_type = "categorical"
            reasoning = "Column has a limited number of repeated values."
        else:
            detected_type = "text"
            reasoning = "Column contains non-numeric values with higher cardinality."

        fallback_schema.append({
            "column_name": name,
            "detected_type": detected_type,
            "reasoning": reasoning,
            "unique_count": unique_count,
            "missing_percent": missing_percent
        })

    fallback_target = str(df.columns[-1]) if len(df.columns) > 0 else ""

    # Call agent
    try:
        result = await call_openrouter_json(MODEL, system_prompt, user_prompt)
        if not isinstance(result, dict):
            logger.error(f"LLM returned non-dictionary response: {type(result)}")
            # Attempt to wrap if it's a list or something else
            result = {"raw_response": result, "schema": fallback_schema, "potential_target": fallback_target}
    except Exception as e:
        logger.error(f"Failed to call LLM for ingestion analysis: {e}")
        result = {
            "schema": fallback_schema,
            "potential_target": fallback_target,
            "target_reasoning": "Selected the final column as a local fallback target.",
            "error": str(e)
        }
    
    # Enrich result with actual counts and sample rows
    result["row_count"] = row_count
    result["column_count"] = col_count
    
    # Get sample rows for overview display (first 5 rows)
    try:
        sample_df = df.head(5).copy()
        # Replace NaN/Inf with None for JSON compatibility
        sample_df = sample_df.replace([np.inf, -np.inf], np.nan)
        # Use where/pd.notnull for more robust NaN -> None conversion across all dtypes
        sample_rows = sample_df.where(pd.notnull(sample_df), None).to_dict(orient="records")
        result["sample_rows"] = sample_rows
    except Exception as e:
        logger.error(f"Failed to generate sample rows: {e}")
        result["sample_rows"] = []
    
    # Ensure mandatory keys exist for orchestrator
    if "potential_target" not in result:
        result["potential_target"] = fallback_target
    if "schema" not in result:
        result["schema"] = fallback_schema
        
    return result
