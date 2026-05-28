import os
import logging
import pandas as pd
import numpy as np
from agents.base_agent import call_openrouter_json

logger = logging.getLogger("CleaningAgent")
MODEL = "meta-llama/llama-3.3-70b-instruct"

async def run_cleaning_agent(df: pd.DataFrame, schema_context: dict) -> tuple[dict, pd.DataFrame]:
    """
    Analyzes data quality issues, decides strategies via LLM,
    applies the cleaning strategies programmatically, and returns the log and cleaned dataframe.
    """
    total_rows = len(df)
    duplicate_count = int(df.duplicated().sum())
    logger.info(f"Cleaning agent analyzing {total_rows} rows.")
    
    # Calculate null counts
    null_counts = {}
    for col in df.columns:
        null_counts[col] = int(df[col].isnull().sum())
    null_counts["total"] = sum(null_counts.values())
    
    # Identify high missing columns (>50%)
    high_missing_cols = [col for col, count in null_counts.items() if col != "total" and (count / total_rows) > 0.5]
    
    # Detect outliers using IQR for numeric columns
    outliers = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        try:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outliers[col] = int(outlier_mask.sum())
        except Exception as e:
            logger.warning(f"Failed to detect outliers for column '{col}': {e}")
            outliers[col] = 0

    # Build prompt for LLM to decide imputation strategies
    system_prompt = (
        "You are an expert Data Cleaning Agent. Your task is to recommend optimal data cleaning strategies "
        "for the columns based on their null values, data types, and unique counts. "
        "Imputation strategies: 'mean' (for normal numeric), 'median' (for skewed numeric), "
        "'mode' (for categorical/boolean), 'drop_column' (if >50% missing or useless), "
        "or 'none' (if no nulls or no action needed). "
        "Respond strictly in valid JSON format."
    )
    
    user_prompt = f"""
Dataset Overview:
Total Rows: {total_rows}
Duplicate Rows: {duplicate_count}
High Missing Columns (>50%): {high_missing_cols}
Missing Count per Column:
{ {k: v for k, v in null_counts.items() if k != 'total' and v > 0} }
Outlier Counts (IQR):
{ {k: v for k, v in outliers.items() if v > 0} }

Recommended column schema types from ingestion agent:
{schema_context.get('schema', [])}

Decide:
1. Imputation strategies for columns with missing values.
2. Whether to drop duplicate rows (always True if duplicate_count > 0).
3. Which columns to drop (including high missing ones).

Return a JSON object containing:
{{
  "imputations": {{
     "column_name": "median | mean | mode | none"
  }},
  "drop_duplicates": true,
  "drop_columns": ["column_to_drop_1"],
  "rationale": "Explanation of cleaning choices made."
}}
"""
    
    # Get cleaning recommendations
    try:
        strategy = await call_openrouter_json(MODEL, system_prompt, user_prompt)
        if not isinstance(strategy, dict):
            logger.error(f"LLM returned non-dictionary strategy: {type(strategy)}")
            strategy = {}
    except Exception as e:
        logger.error(f"Failed to call LLM for cleaning strategy: {e}")
        strategy = {}
    
    # Programmatically apply the cleaning recommendations to df
    cleaned_df = df.copy()
    cleaning_log = []
    
    # 1. Drop duplicates
    if strategy.get("drop_duplicates", True) and duplicate_count > 0:
        cleaned_df = cleaned_df.drop_duplicates()
        cleaning_log.append(f"Dropped {duplicate_count} duplicate rows.")
        
    # 2. Drop designated columns
    cols_to_drop = strategy.get("drop_columns", [])
    if not isinstance(cols_to_drop, list):
        cols_to_drop = []
        
    # Always drop cols with >50% missing if not already designated
    for c in high_missing_cols:
        if c not in cols_to_drop:
            cols_to_drop.append(c)
            
    # SAFEGUARD: Never drop the potential target column
    target = schema_context.get("potential_target", "")
    if target in cols_to_drop:
        cols_to_drop.remove(target)
        cleaning_log.append(f"Safeguard: Prevented dropping the target column '{target}'.")
            
    cols_to_drop = [c for c in cols_to_drop if c in cleaned_df.columns]
    if cols_to_drop:
        cleaned_df = cleaned_df.drop(columns=cols_to_drop)
        for col in cols_to_drop:
            cleaning_log.append(f"Dropped column '{col}' due to high missing values (>50%) or LLM recommendation.")
            
    # 3. Apply imputations
    imputations = strategy.get("imputations", {})
    if not isinstance(imputations, dict):
        imputations = {}
        
    for col, method in imputations.items():
        if col not in cleaned_df.columns:
            continue
        
        col_nulls = int(cleaned_df[col].isnull().sum())
        if col_nulls == 0:
            continue
            
        try:
            if method == "mean":
                val = cleaned_df[col].mean()
                cleaned_df[col] = cleaned_df[col].fillna(val)
                cleaning_log.append(f"Imputed {col_nulls} missing values in '{col}' with mean ({val:.2f}).")
            elif method == "median":
                val = cleaned_df[col].median()
                cleaned_df[col] = cleaned_df[col].fillna(val)
                cleaning_log.append(f"Imputed {col_nulls} missing values in '{col}' with median ({val:.2f}).")
            elif method == "mode":
                val_series = cleaned_df[col].mode()
                if not val_series.empty:
                    val = val_series[0]
                    cleaned_df[col] = cleaned_df[col].fillna(val)
                    cleaning_log.append(f"Imputed {col_nulls} missing values in '{col}' with mode ({val}).")
                else:
                    cleaning_log.append(f"Tried mode imputation on '{col}', but column has no mode. Left uncleaned.")
        except Exception as e:
            logger.warning(f"Failed to impute column '{col}' with method '{method}': {e}")
            continue

    # Ensure other nulls are filled with a generic fallback mode/median if they were missed
    for col in cleaned_df.columns:
        nulls = int(cleaned_df[col].isnull().sum())
        if nulls > 0:
            try:
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    val = cleaned_df[col].median()
                    if not pd.isna(val):
                        cleaned_df[col] = cleaned_df[col].fillna(val)
                        cleaning_log.append(f"Imputed remaining {nulls} missing values in numeric '{col}' with median ({val:.2f}) [Fallback].")
                else:
                    val_series = cleaned_df[col].mode()
                    if not val_series.empty:
                        val = val_series[0]
                        cleaned_df[col] = cleaned_df[col].fillna(val)
                        cleaning_log.append(f"Imputed remaining {nulls} missing values in categorical '{col}' with mode ({val}) [Fallback].")
            except Exception as e:
                logger.warning(f"Fallback imputation failed for column '{col}': {e}")
                    
    # Construct before/after summary
    result = {
        "null_counts": null_counts,
        "duplicate_count": duplicate_count,
        "outlier_columns": [col for col, count in outliers.items() if count > 0],
        "outlier_counts": outliers,
        "cleaning_log": cleaning_log,
        "cleaned_shape": [int(cleaned_df.shape[0]), int(cleaned_df.shape[1])],
        "rationale": strategy.get("rationale", "Successfully cleaned dataset.")
    }
    
    return result, cleaned_df
