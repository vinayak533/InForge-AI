import os
from agents.base_agent import call_groq

MODEL = "llama-3.3-70b-versatile"

async def run_code_agent(previous_context: dict) -> str:
    """
    Calls Llama-3.3-70b via Groq to generate a self-contained executable Python script
    matching the exact details of this dataset analysis.
    """
    row_count = previous_context.get("ingestion_agent", {}).get("row_count", "N/A")
    col_count = previous_context.get("ingestion_agent", {}).get("column_count", "N/A")
    schema = previous_context.get("ingestion_agent", {}).get("schema", [])
    
    clean_log = previous_context.get("cleaning_agent", {}).get("cleaning_log", [])
    null_counts = previous_context.get("cleaning_agent", {}).get("null_counts", {})
    duplicate_count = previous_context.get("cleaning_agent", {}).get("duplicate_count", 0)
    
    top_correlations = previous_context.get("eda_agent", {}).get("top_correlations", [])
    
    ml_task = previous_context.get("ml_agent", {}).get("task_type", "clustering")
    best_model = previous_context.get("ml_agent", {}).get("best_model", "N/A")
    best_score = previous_context.get("ml_agent", {}).get("best_score", "N/A")
    ml_results = previous_context.get("ml_agent", {}).get("model_results", [])
    
    insights = previous_context.get("insights_agent", {}).get("insights", [])
    exec_summary = previous_context.get("insights_agent", {}).get("executive_summary", "")

    system_prompt = (
        "You are an elite Software Engineer and Data Scientist. Your objective is to write a single, complete, "
        "production-grade, and beautifully commented Python script that fully reproduces a data analytics pipeline. "
        "The script must load the data (mock dataset or dynamic path), perform the exact cleaning steps, EDA, "
        "generate and save the charts, and train and evaluate the best machine learning model. "
        "Make sure to include markdown-style headers, extensive comments, clean code structuring, and proper imports. "
        "Output ONLY the raw Python code. Do not wrap it in markdown code block comments, do not add introductory text."
    )
    
    user_prompt = f"""
Dataset Details:
- Dimensions: {row_count} rows, {col_count} columns
- Schema: {schema}

Pipeline Executed:
1. Data Quality Actions:
   - Duplicates found: {duplicate_count}
   - Null values: {null_counts.get('total', 0)}
   - Executed clean steps: {clean_log}
2. Exploratory Data Analysis:
   - Top correlations: {top_correlations}
3. Machine Learning:
   - Task type: {ml_task}
   - Best model: {best_model} with score {best_score}
   - Compared models: {ml_results}
4. Synthesized Business Value:
   - Summary: {exec_summary}
   - Insights: {insights}

Write a clean, runnable, well-commented, complete Python script (using pandas, numpy, scikit-learn, xgboost, matplotlib, and seaborn) that replicates these exact pipeline actions.
The script should assume it reads a dataset from a command line argument or a path variable 'dataset.csv' (with fallback to a generated mock dataset matching the schema so it is instantly runnable).
Generate the same types of charts (correlation heatmap, target boxplot, scatterplot of top correlation, etc.) and save them as local PNG files.
Print a final report at the end of the script containing the KPIs and comparative ML metrics.
Return ONLY the raw runnable script text. No headers, no footers, no conversational intro.
"""
    
    # Get raw script
    script = await call_groq(MODEL, system_prompt, user_prompt, temperature=0.1)
    
    # Strip markdown wrappers if the model ignored the instructions and included them
    if script.strip().startswith("```"):
        import re
        match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", script)
        if match:
            script = match.group(1).strip()
            
    return script
