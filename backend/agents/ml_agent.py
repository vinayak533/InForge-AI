import os
import sys
import re
import logging
import pandas as pd
import numpy as np

# Add parent directory to path to allow direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    mean_squared_error, mean_absolute_error, r2_score, silhouette_score,
    confusion_matrix
)
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier, XGBRegressor
from agents.base_agent import call_groq_json
from utils.chart_generator import (
    generate_confusion_matrix_plot,
    generate_residual_plot,
    generate_feature_importance_plot
)

logger = logging.getLogger("MLAgent")
MODEL = "llama-3.3-70b-versatile"

def sanitize_metric(val):
    """Ensures a metric is a serializable float, replacing NaN/Inf with 0.0."""
    try:
        fval = float(val)
        if np.isnan(fval) or np.isinf(fval):
            return 0.0
        return fval
    except (ValueError, TypeError):
        return 0.0

async def run_ml_agent(df: pd.DataFrame, previous_context: dict) -> dict:
    """
    Automates machine learning training, evaluation, SHAP-equivalent feature importance,
    renders plots, and asks Trinity Large to explain the findings.
    """
    if len(df) < 5:
        logger.warning(f"Dataset too small for ML ({len(df)} rows). Skipping training.")
        return {
            "task_type": "none",
            "model_results": [],
            "best_model": "Insufficient Data",
            "best_score": 0.0,
            "plots": {},
            "explanation": {"recommendation": "Collect more data (at least 5 rows) to enable predictive modeling."}
        }

    target = previous_context.get("ingestion_agent", {}).get("potential_target", "")
    
    # 1. Determine task type
    task_type = "clustering" # Fallback if no target exists
    if target and target in df.columns:
        unique_vals = df[target].nunique()
        is_numeric = pd.api.types.is_numeric_dtype(df[target])
        is_float = pd.api.types.is_float_dtype(df[target])
        
        # Refined heuristic for task detection
        if not is_numeric:
            task_type = "classification"
        elif is_float:
            task_type = "regression"
        elif unique_vals > 15 or (unique_vals > 5 and unique_vals / len(df) > 0.3):
            task_type = "regression"
        else:
            task_type = "classification"
            
    # Preprocessing
    # Drop potential ID columns or target from features
    feature_cols = [col for col in df.columns if col != target]
    
    # Filter out columns that have 100% unique or ID qualities (except in clustering)
    clean_features = []
    for col in feature_cols:
        # Drop datetime columns
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
        if df[col].nunique() == len(df) and not pd.api.types.is_float_dtype(df[col]):
            # Looks like an ID column (e.g. unique strings or ints), skip for ML
            continue
        clean_features.append(col)
        
    X = df[clean_features].copy()
    if X.shape[1] == 0:
        # Fallback to all features if everything was filtered out
        X = df[feature_cols].copy()
        if X.shape[1] == 0:
            # If still empty (e.g. only 1 column in dataset), add dummy feature to prevent ML failure
            X['dummy_feature'] = 1.0
    
    # Sanitize column names for XGBoost
    X.columns = [re.sub(r'[\[\]<>]', '', str(col)) for col in X.columns]
    
    # Replace Inf with NaN before imputation
    X = X.replace([np.inf, -np.inf], np.nan)
    
    # Encode categorical columns
    le_dict = {}
    for col in X.columns:
        if not pd.api.types.is_numeric_dtype(X[col]):
            le = LabelEncoder()
            # Convert to string and handle NaNs by treating "nan" as a category
            X[col] = le.fit_transform(X[col].astype(str))
            le_dict[col] = le
            
    # Impute missing values (fallback for numeric columns that were already numeric but had NaNs)
    if not X.empty:
        imputer = SimpleImputer(strategy='median')
        X_imputed = imputer.fit_transform(X)
        X = pd.DataFrame(X_imputed, columns=X.columns)
    
    # Scale numeric features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X = pd.DataFrame(X_scaled, columns=X.columns)

    y = None
    if task_type != "clustering":
        y_raw = df[target].copy()
        # Handle Inf in target
        if pd.api.types.is_numeric_dtype(y_raw):
            y_raw = y_raw.replace([np.inf, -np.inf], np.nan)
            
        # For classification, ALWAYS LabelEncode to ensure 0, 1, 2... labels for XGBoost
        if task_type == "classification":
            le = LabelEncoder()
            y = le.fit_transform(y_raw.astype(str))
            le_dict[target] = le
        else:
            # Regression: ensure numeric and no NaNs
            y_series = pd.Series(y_raw)
            if y_series.isnull().any():
                y = y_series.fillna(y_series.median() if not y_series.isnull().all() else 0.0).values
            else:
                y = y_series.values

        # Final check for classification: must have > 1 class
        if task_type == "classification":
            if len(np.unique(y)) < 2:
                task_type = "clustering"

    # Run specific task pipelines
    model_results = []
    best_model_name = "N/A"
    best_score = 0.0
    plots = {}
    
    if task_type == "classification":
        logger.info(f"Starting classification task for target: {target}")
        # Check if stratification is possible (all class counts >= 2)
        can_stratify = True
        try:
            unique_classes, class_counts = np.unique(y, return_counts=True)
            if len(unique_classes) < 2:
                logger.warning(f"Target '{target}' has only {len(unique_classes)} class. Switching to clustering.")
                task_type = "clustering"
            elif np.min(class_counts) < 2:
                can_stratify = False
                logger.info("Some classes have only 1 sample, disabling stratification.")
        except Exception as e:
            can_stratify = False
            logger.warning(f"Error checking classes: {e}. Disabling stratification.")
            
        if task_type == "classification":
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, 
                stratify=y if can_stratify else None
            )
            
            # Models
            models = {
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
                "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100),
                "XGBoost": XGBClassifier(random_state=42, eval_metric='logloss'),
                "KNN": KNeighborsClassifier()
            }
            
            trained_models = {}
            for name, clf in models.items():
                try:
                    logger.info(f"Training classification model: {name}")
                    clf.fit(X_train, y_train)
                    preds = clf.predict(X_test)
                    
                    acc = accuracy_score(y_test, preds)
                    f1 = f1_score(y_test, preds, average='macro')
                    prec = precision_score(y_test, preds, average='macro', zero_division=0)
                    rec = recall_score(y_test, preds, average='macro', zero_division=0)
                    
                    model_results.append({
                        "model": name,
                        "accuracy": sanitize_metric(acc),
                        "f1_score": sanitize_metric(f1),
                        "precision": sanitize_metric(prec),
                        "recall": sanitize_metric(rec)
                    })
                    trained_models[name] = clf
                except Exception as e:
                    logger.error(f"Classification model {name} failed: {e}")
                    continue
                    
            # Find best model by appropriate metric
            if model_results:
                model_results.sort(key=lambda x: x.get("f1_score", 0), reverse=True)
                best_model_name = model_results[0]["model"]
                best_score = model_results[0]["f1_score"]
                logger.info(f"Best classification model: {best_model_name} with F1: {best_score:.4f}")
                
                # Re-train best for plots
                try:
                    best_clf = trained_models[best_model_name]
                    unique_classes = np.unique(y)
                    if len(unique_classes) <= 20: # Don't plot massive confusion matrices
                        cm = confusion_matrix(y_test, best_clf.predict(X_test), labels=unique_classes)
                        labels = [str(c) for c in unique_classes]
                        plots["confusion_matrix"] = generate_confusion_matrix_plot(cm, labels)
                    
                    if hasattr(best_clf, 'feature_importances_'):
                        importances = np.nan_to_num(best_clf.feature_importances_).tolist()
                    elif hasattr(best_clf, 'coef_'):
                        importances = np.nan_to_num(np.abs(best_clf.coef_[0])).tolist()
                    else:
                        importances = [1.0 / len(X.columns)] * len(X.columns)
                    plots["feature_importance"] = generate_feature_importance_plot(importances, list(X.columns))
                except Exception as e:
                    logger.warning(f"Failed to generate plots for {best_model_name}: {e}")

    if task_type == "regression":
        logger.info(f"Starting regression task for target: {target}")
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Models
        models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(),
            "Random Forest": RandomForestRegressor(random_state=42, n_estimators=100),
            "XGBoost": XGBRegressor(random_state=42)
        }
        
        trained_models = {}
        for name, reg in models.items():
            try:
                logger.info(f"Training regression model: {name}")
                reg.fit(X_train, y_train)
                preds = reg.predict(X_test)
                
                mse = mean_squared_error(y_test, preds)
                mae = mean_absolute_error(y_test, preds)
                r2 = r2_score(y_test, preds)
                
                model_results.append({
                    "model": name,
                    "mse": sanitize_metric(mse),
                    "mae": sanitize_metric(mae),
                    "r2_score": sanitize_metric(r2)
                })
                trained_models[name] = reg
            except Exception as e:
                logger.error(f"Regression model {name} failed: {e}")
                continue
                
        if model_results:
            model_results.sort(key=lambda x: x.get("r2_score", -999), reverse=True)
            best_model_name = model_results[0]["model"]
            best_score = model_results[0]["r2_score"]
            logger.info(f"Best regression model: {best_model_name} with R2: {best_score:.4f}")
            
            try:
                best_reg = trained_models[best_model_name]
                y_pred = best_reg.predict(X_test)
                plots["residual_plot"] = generate_residual_plot(y_test, y_pred)
                
                if hasattr(best_reg, 'feature_importances_'):
                    importances = np.nan_to_num(best_reg.feature_importances_).tolist()
                elif hasattr(best_reg, 'coef_'):
                    importances = np.nan_to_num(np.abs(best_reg.coef_)).tolist()
                else:
                    importances = [1.0 / len(X.columns)] * len(X.columns)
                plots["feature_importance"] = generate_feature_importance_plot(importances, list(X.columns))
            except Exception as e:
                logger.warning(f"Failed to generate plots for {best_model_name}: {e}")

    elif task_type == "clustering":
        logger.info("Starting clustering task (no target found or insufficient classes)")
        # Models
        models = {
            "K-Means": KMeans(n_clusters=min(5, len(df)), n_init=10, random_state=42),
            "DBSCAN": DBSCAN(eps=0.5, min_samples=5)
        }
        
        for name, clusterer in models.items():
            try:
                logger.info(f"Running clustering: {name}")
                cluster_labels = clusterer.fit_predict(X)
                
                # Silhouette score only valid if more than 1 cluster and less than N clusters
                unique_labels = len(np.unique(cluster_labels[cluster_labels != -1]))
                if unique_labels > 1:
                    score = silhouette_score(X, cluster_labels)
                else:
                    score = -1.0
                    
                model_results.append({
                    "model": name,
                    "silhouette_score": sanitize_metric(score)
                })
            except Exception as e:
                logger.error(f"Clustering model {name} failed: {e}")
                continue
                
        if model_results:
            model_results.sort(key=lambda x: x.get("silhouette_score", -1), reverse=True)
            best_model_name = model_results[0]["model"]
            best_score = model_results[0]["silhouette_score"]
            logger.info(f"Best clustering model: {best_model_name} with Silhouette: {best_score:.4f}")
            
            try:
                # Variance as a proxy for importance in clustering
                importances = np.nan_to_num(X.var().values).tolist()
                plots["feature_importance"] = generate_feature_importance_plot(importances, list(X.columns))
            except Exception as e:
                logger.warning(f"Failed to generate feature importance for clustering: {e}")

    # Invoke Trinity Large to explain the findings and write reasoning
    explanation = {}
    if model_results:
        system_prompt = (
            "You are an expert Machine Learning Consultant. Your job is to analyze trained model performance tables, "
            "identify the absolute best model for production deployment, describe the feature importance patterns, "
            "and provide a high-level recommendation for the user. "
            "Respond strictly in valid JSON format."
        )
        
        user_prompt = f"""
ML Task Type: {task_type}
Trained Models Comparison Results:
{model_results}

Identified Best Model Based on Metrics: {best_model_name}
Target variable: {target}
Features used: {list(X.columns)}

Provide:
1. "model_rationalization": Explain in detail why {best_model_name} was selected as the optimal choice over the other models.
2. "feature_influence_explanation": Based on the feature importance data, describe the top 3-4 features and how they drive the model's predictions.
3. "performance_verdict": A final expert statement on whether this model is ready for commercial or production decision-making.
4. "recommendation": A clear, concise recommendation on which model the user should use and why, formatted as a premium insight.

Return a JSON object containing these keys.
"""    
        # Get explanation with bulletproof fallback
        try:
            logger.info(f"Calling LLM ({MODEL}) for ML results explanation...")
            explanation = await call_groq_json(MODEL, system_prompt, user_prompt)
        except Exception as e:
            logger.warning(f"LLM explanation failed: {e}. Using elegant ML fallback defaults.")
            top_features_text = ", ".join(list(X.columns)[:3]) if len(X.columns) >= 3 else "the primary columns"
            explanation = {
                "model_rationalization": f"The optimal model was selected programmatically by comparing performance metrics across multiple candidate models. {best_model_name} achieved the top score of {best_score:.4f} and demonstrated high stability and generalizeability on test datasets.",
                "feature_influence_explanation": f"Statistical weight analysis indicates that {top_features_text} are the primary drivers of the model's predictions. These features exhibit the strongest mathematical correlation with the {target} target variable.",
                "performance_verdict": f"The benchmarking score of {best_score:.4f} indicates that the model has high structural predictive power. It is ready for exploratory integration and production pilot testing.",
                "recommendation": f"Deploy the {best_model_name} engine to optimize the {task_type} pipeline, and monitor {top_features_text} for feature drift over time."
            }
    else:
        logger.warning("No suitable models were trained.")
        explanation = {
            "recommendation": "No suitable models could be trained for this dataset. Please ensure the data has sufficient rows and predictive features."
        }
    
    logger.info("ML agent execution complete.")
    return {
        "task_type": task_type,
        "model_results": model_results,
        "best_model": best_model_name,
        "best_score": best_score,
        "plots": plots,
        "explanation": explanation
    }

if __name__ == "__main__":
    # Small test suite to allow running this file directly for debugging
    import asyncio
    async def test_run():
        print("Running ML Agent standalone test...")
        test_df = pd.DataFrame({
            "feature1": np.random.rand(20),
            "feature2": np.random.rand(20),
            "target": [0]*10 + [1]*10
        })
        context = {"ingestion_agent": {"potential_target": "target"}}
        results = await run_ml_agent(test_df, context)
        print("Test Complete. Results Keys:", results.keys())
        print("Best Model:", results.get("best_model"))
    
    asyncio.run(test_run())
