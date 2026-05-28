import os
import pandas as pd
import numpy as np
from agents.base_agent import call_openrouter_json

MODEL = "meta-llama/llama-3.3-70b-instruct"

async def run_eda_agent(df: pd.DataFrame, previous_context: dict) -> dict:
    """
    Computes statistical details (stats, correlation, skewness, zero-variance columns) programmatically,
    and calls Nemotron-3 to get rich textual descriptions.
    """
    # 1. Descriptive stats for numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    stats = {}
    if not numeric_df.empty:
        desc = numeric_df.describe()
        for col in numeric_df.columns:
            stats[col] = {
                "count": int(desc[col]["count"]),
                "mean": float(desc[col]["mean"]),
                "std": float(desc[col]["std"]) if not pd.isna(desc[col]["std"]) else 0.0,
                "min": float(desc[col]["min"]),
                "q25": float(desc[col]["25%"]),
                "median": float(desc[col]["50%"]),
                "q75": float(desc[col]["75%"]),
                "max": float(desc[col]["max"]),
                "skew": float(numeric_df[col].skew()) if not pd.isna(numeric_df[col].skew()) else 0.0,
                "kurtosis": float(numeric_df[col].kurtosis()) if not pd.isna(numeric_df[col].kurtosis()) else 0.0
            }

    # 2. Categorical value counts (top 5 categories for each non-numeric column)
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    cat_counts = {}
    for col in categorical_cols:
        counts = df[col].value_counts().head(5)
        cat_counts[col] = {str(k): int(v) for k, v in counts.items()}

    # 3. Correlation matrix & Top Correlations
    corr_matrix = {}
    top_correlations = []
    if numeric_df.shape[1] >= 2:
        corr = numeric_df.corr()
        # Build serializable matrix
        for col in corr.columns:
            corr_matrix[col] = {c: float(v) if not pd.isna(v) else 0.0 for c, v in corr[col].items()}
            
        # Identify top correlated pairs
        pairs = []
        cols = corr.columns
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                val = corr.iloc[i, j]
                if not pd.isna(val):
                    pairs.append(((cols[i], cols[j]), float(val)))
        
        # Sort by absolute value
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        for (c1, c2), val in pairs[:5]:
            top_correlations.append({
                "feature_1": c1,
                "feature_2": c2,
                "correlation": val
            })

    # 4. Zero variance columns (useless features)
    zero_variance_cols = []
    for col in df.columns:
        if df[col].nunique() <= 1:
            zero_variance_cols.append(col)

    # 5. Skewed columns badge trigger (skew > 1 or < -1)
    skewed_columns = []
    for col, st in stats.items():
        if abs(st["skew"]) > 1.0:
            skewed_columns.append({
                "column": col,
                "skewness": st["skew"]
            })

    # Call Nemotron-3 to synthesize statistical insights
    system_prompt = (
        "You are an expert Exploratory Data Analysis (EDA) Agent. Your role is to examine calculated dataset "
        "statistics, correlations, and distributions, and synthesize an expert analytical summary. "
        "Discuss major correlations, skewed columns, distribution implications, and data quality indicators. "
        "Provide responses strictly in valid JSON format."
    )
    
    user_prompt = f"""
Calculated Descriptive Statistics:
{ {k: {"mean": v["mean"], "median": v["median"], "skew": v["skew"]} for k, v in stats.items()} }

Top Correlated Feature Pairs:
{top_correlations}

Categorical Value Counts:
{cat_counts}

Zero Variance Columns:
{zero_variance_cols}

Skewed Columns:
{skewed_columns}

Return a JSON object containing:
{{
  "distribution_analysis": "A brief overview explaining key features' distributions, skewness, and their business meaning.",
  "correlation_analysis": "A brief explanation of what the top correlations tell us about the patterns in the data.",
  "flags_analysis": "Comments on zero-variance columns or high-skew variables, explaining why they might cause issues or how they should be handled."
}}
"""
    
    # Get verbal summary
    textual_insights = await call_openrouter_json(MODEL, system_prompt, user_prompt)
    
    # Combine stats and text into a single context response
    result = {
        "descriptive_stats": stats,
        "categorical_counts": cat_counts,
        "correlation_matrix": corr_matrix,
        "top_correlations": top_correlations,
        "skewed_columns": skewed_columns,
        "zero_variance_columns": zero_variance_cols,
        "textual_insights": textual_insights
    }
    
    return result
