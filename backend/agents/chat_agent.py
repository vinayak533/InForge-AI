import os
import json
import httpx
from agents.base_agent import call_groq

MODEL = "llama-3.3-70b-versatile"

def _fmt_score(value):
    if isinstance(value, (int, float)):
        return f"{value:.3f}"
    return str(value)

def _local_chat_answer(question: str, context_summary: dict) -> str:
    question_l = question.lower()
    lines = []

    if any(token in question_l for token in ["model", "ml", "machine", "score", "accuracy", "best"]):
        lines.append(f"Best model: {context_summary['best_predictive_model']}")
        lines.append("Reason: it ranked highest on the pipeline's primary benchmark metric for the detected ML task.")
        model_results = context_summary.get("all_model_results", [])
        if model_results:
            lines.append("\nModel comparison:")
            for row in model_results[:6]:
                metrics = [f"{k}: {_fmt_score(v)}" for k, v in row.items() if k != "model"]
                lines.append(f"- {row.get('model', 'Model')}: {', '.join(metrics)}")

    elif any(token in question_l for token in ["correlation", "relationship", "related"]):
        correlations = context_summary.get("strongest_correlations", [])
        if correlations:
            lines.append("Strongest correlations:")
            for item in correlations[:5]:
                lines.append(
                    f"- {item.get('feature_1')} and {item.get('feature_2')}: "
                    f"{_fmt_score(item.get('correlation'))}"
                )
        else:
            lines.append("No strong numeric correlations were available in the completed analysis.")

    elif any(token in question_l for token in ["clean", "quality", "missing", "duplicate", "null"]):
        actions = context_summary.get("cleaning_actions_taken", [])
        if actions:
            lines.append("Data quality actions:")
            lines.extend(f"- {action}" for action in actions[:8])
        else:
            lines.append("No major cleaning actions were required or recorded.")

    elif any(token in question_l for token in ["feature", "column", "important"]):
        lines.append(f"Dataset size: {context_summary['dataset_dimensions']}")
        lines.append(f"Detected target: {context_summary['detected_target']}")
        correlations = context_summary.get("strongest_correlations", [])
        if correlations:
            lines.append("Important feature relationships:")
            for item in correlations[:5]:
                lines.append(
                    f"- {item.get('feature_1')} / {item.get('feature_2')}: "
                    f"{_fmt_score(item.get('correlation'))}"
                )
        else:
            lines.append("No ranked feature relationships were available from correlation analysis.")

    else:
        summary = context_summary.get("dataset_executive_summary")
        if summary:
            lines.append(summary)
        else:
            lines.append(
                f"The analysis completed for {context_summary['dataset_dimensions']} "
                f"with target `{context_summary['detected_target']}`."
            )
        insights = context_summary.get("business_insights", [])
        if insights:
            lines.append("\nKey insights:")
            lines.extend(f"- {insight}" for insight in insights[:5])
        recs = context_summary.get("recommended_business_actions", [])
        if recs:
            lines.append("\nRecommended actions:")
            lines.extend(f"- {rec}" for rec in recs[:3])

    return "\n".join(lines)

async def run_chat_agent(question: str, history: list[dict], pipeline_context: dict) -> str:
    """
    Handles context-enriched conversation between the user and Qwen3-32b via Groq
    regarding the dataset analysis outcomes.
    """
    # Build a compact summary of the pipeline outcomes to fit in prompt context
    row_count = pipeline_context.get("row_count", "N/A")
    col_count = pipeline_context.get("column_count", "N/A")
    target = pipeline_context.get("potential_target", "N/A")
    
    clean_agent = pipeline_context.get("cleaning_agent", {})
    clean_log = clean_agent.get("cleaning_log", [])
    
    eda_agent = pipeline_context.get("eda_agent", {})
    top_correlations = eda_agent.get("top_correlations", [])
    
    ml_agent = pipeline_context.get("ml_agent", {})
    best_model = ml_agent.get("best_model", "N/A")
    best_score = ml_agent.get("best_score", "N/A")
    ml_results = ml_agent.get("model_results", [])
    
    insights_agent = pipeline_context.get("insights_agent", {})
    summary = insights_agent.get("executive_summary", "")
    insights = insights_agent.get("insights", [])
    recs = insights_agent.get("recommendations", [])

    context_summary = {
        "dataset_dimensions": f"{row_count} rows, {col_count} columns",
        "detected_target": target,
        "cleaning_actions_taken": clean_log,
        "strongest_correlations": top_correlations,
        "best_predictive_model": f"{best_model} (score: {best_score})",
        "all_model_results": ml_results,
        "dataset_executive_summary": summary,
        "business_insights": insights,
        "recommended_business_actions": recs
    }

    system_prompt = (
        "You are an elite, highly professional AI Data Analyst floating chatbot assistant. "
        "Your role is to answer any natural language questions about the user's uploaded dataset, "
        "relying strictly on the compiled analytical findings context. "
        "Tone: Silent, powerful, highly professional, direct. Do not use generic filler words, "
        "over-polite introductions, or buzzwords. "
        "If a user asks for data columns, statistics, or ML results, answer with crisp markdown tables "
        "or compact bullet lists. Never output agent internal names or model names in the UI. "
        "Keep answers extremely professional and factual."
    )
    
    # Construct conversation prompt with history and context
    history_str = ""
    for msg in history[-8:]: # Keep last 8 turns of history
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role_label}: {msg['content']}\n"
        
    user_prompt = f"""
Analytical Context of Dataset:
{json.dumps(context_summary, indent=2)}

Conversation History:
{history_str}
User's Latest Question: {question}

Answer the latest question in a highly informative and professional manner, grounding your responses in the analytical context above.
"""
    
    try:
        response = await call_groq(MODEL, system_prompt, user_prompt, temperature=0.5)
        return response
    except Exception:
        return _local_chat_answer(question, context_summary)
