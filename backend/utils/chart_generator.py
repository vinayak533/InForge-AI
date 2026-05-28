import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from matplotlib.figure import Figure
import seaborn as sns
import io
import base64
import numpy as np
import pandas as pd

# Global visual parameters matching InForge AI design system
BG_COLOR = '#080B14'
CARD_BG = '#0E1320'
BORDER_COLOR = '#1C2333'
TEXT_PRIMARY = '#F0F4FF'
TEXT_SECONDARY = '#8B9CC8'
COLOR_CYAN = '#00D4FF'
COLOR_BLUE = '#0080FF'
COLOR_SUCCESS = '#00E5A0'
COLOR_WARNING = '#FFB340'
COLOR_ERROR = '#FF4D6A'

PALETTE = [COLOR_CYAN, COLOR_BLUE, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR, '#9B51E0', '#FF85A2', '#2EC4B6']

def apply_dark_theme_to_fig(fig):
    """
    Applies the InForge AI dark theme to a specific Matplotlib figure.
    """
    fig.patch.set_facecolor(BG_COLOR)
    for ax in fig.get_axes():
        ax.set_facecolor(CARD_BG)
        ax.spines['bottom'].set_color(BORDER_COLOR)
        ax.spines['top'].set_color(BORDER_COLOR)
        ax.spines['right'].set_color(BORDER_COLOR)
        ax.spines['left'].set_color(BORDER_COLOR)
        ax.tick_params(axis='x', colors=TEXT_SECONDARY)
        ax.tick_params(axis='y', colors=TEXT_SECONDARY)
        ax.yaxis.label.set_color(TEXT_SECONDARY)
        ax.xaxis.label.set_color(TEXT_SECONDARY)
        ax.title.set_color(TEXT_PRIMARY)
        ax.grid(True, linestyle='--', alpha=0.3, color=BORDER_COLOR)

def fig_to_base64(fig) -> str:
    """
    Converts a Matplotlib figure to a base64 encoded PNG string.
    Uses lower DPI (100) to minimize memory usage and payload size.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor=BG_COLOR)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str

def generate_correlation_heatmap(df: pd.DataFrame) -> str:
    """
    Generates a dark-themed correlation heatmap using OO API.
    """
    numeric_cols = df.select_dtypes(include=[np.number])
    if numeric_cols.shape[1] < 2:
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Insufficient numeric columns for correlation heatmap", 
                ha='center', va='center', color=TEXT_SECONDARY, fontsize=12)
        ax.axis('off')
        apply_dark_theme_to_fig(fig)
        return fig_to_base64(fig)

    corr = numeric_cols.corr()
    fig = Figure(figsize=(min(8, corr.shape[1]*1.2), min(6, corr.shape[0]*1.0)))
    ax = fig.add_subplot(111)
    
    cmap = sns.diverging_palette(220, 180, as_cmap=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap, vmin=-1, vmax=1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .8}, ax=ax)
    
    ax.set_title("Feature Correlation Matrix", fontsize=14, pad=15)
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_distribution_plot(df: pd.DataFrame, col: str) -> str:
    """
    Generates a distribution histogram + KDE using OO API.
    """
    fig = Figure(figsize=(7, 4.5))
    ax = fig.add_subplot(111)
    
    data = df[col].dropna()
    sns.histplot(data, kde=True, color=COLOR_CYAN, ax=ax, stat='density', alpha=0.4, edgecolor=BG_COLOR)
    sns.kdeplot(data, color=COLOR_BLUE, ax=ax, linewidth=2)
    
    ax.set_title(f"Distribution of {col}", fontsize=14, pad=15)
    ax.set_xlabel(col)
    ax.set_ylabel("Density")
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_box_plot(df: pd.DataFrame, col: str, group_col: str = None) -> str:
    """
    Generates a box plot using OO API.
    """
    fig = Figure(figsize=(7, 4.5))
    ax = fig.add_subplot(111)
    
    if group_col and df[group_col].nunique() <= 10:
        n_groups = df[group_col].nunique()
        sns.boxplot(x=group_col, y=col, data=df, ax=ax, hue=group_col, palette=PALETTE[:n_groups], width=0.5, legend=False, flierprops={"markerfacecolor": COLOR_ERROR, "markeredgecolor": BORDER_COLOR})
        ax.set_xlabel(group_col)
    else:
        sns.boxplot(y=col, data=df, ax=ax, color=COLOR_CYAN, width=0.3, flierprops={"markerfacecolor": COLOR_ERROR, "markeredgecolor": BORDER_COLOR})
        ax.set_xlabel("")
        
    ax.set_title(f"Box Plot of {col}" + (f" by {group_col}" if group_col else ""), fontsize=14, pad=15)
    ax.set_ylabel(col)
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_bar_chart(df: pd.DataFrame, col: str) -> str:
    """
    Generates a horizontal bar chart using OO API.
    """
    fig = Figure(figsize=(7, 4.5))
    ax = fig.add_subplot(111)
    
    counts = df[col].value_counts().head(10)
    n_items = len(counts)
    sns.barplot(x=counts.values, y=counts.index.astype(str), ax=ax, hue=counts.index.astype(str), palette=PALETTE[:n_items], orient='h', legend=False)
    
    ax.set_title(f"Top 10 Value Counts: {col}", fontsize=14, pad=15)
    ax.set_xlabel("Count")
    ax.set_ylabel(col)
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, hue_col: str = None) -> str:
    """
    Generates a scatter plot using OO API.
    """
    fig = Figure(figsize=(7, 4.5))
    ax = fig.add_subplot(111)
    
    if hue_col and df[hue_col].nunique() <= 8:
        n_hues = df[hue_col].nunique()
        sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, palette=PALETTE[:n_hues], alpha=0.8, ax=ax, s=50, edgecolor=BG_COLOR)
        ax.legend(facecolor=CARD_BG, edgecolor=BORDER_COLOR, labelcolor=TEXT_PRIMARY)
    else:
        sns.scatterplot(data=df, x=x_col, y=y_col, color=COLOR_CYAN, alpha=0.8, ax=ax, s=50, edgecolor=BG_COLOR)
        
    ax.set_title(f"{x_col} vs {y_col}", fontsize=14, pad=15)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_missing_heatmap(df: pd.DataFrame) -> str:
    """
    Generates a missing values heatmap using OO API.
    """
    fig = Figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    
    missing_mask = df.isnull()
    
    if missing_mask.sum().sum() == 0:
        ax.text(0.5, 0.5, "No missing values detected in dataset!", 
                ha='center', va='center', color=COLOR_SUCCESS, fontsize=12, weight='bold')
        ax.axis('off')
        apply_dark_theme_to_fig(fig)
        return fig_to_base64(fig)
        
    cmap = sns.color_palette([CARD_BG, COLOR_WARNING])
    sns.heatmap(missing_mask, yticklabels=False, cbar=False, cmap=cmap, ax=ax)
    
    ax.set_title("Missing Values Map (Highlighted in Orange)", fontsize=14, pad=15)
    ax.set_xlabel("Columns")
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_confusion_matrix_plot(cm: np.ndarray, labels: list) -> str:
    """
    Generates confusion matrix plot for classification models using OO API.
    """
    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)
    
    cmap = sns.light_palette(COLOR_CYAN, as_cmap=True)
    sns.heatmap(cm, annot=True, fmt="d", cmap=cmap, xticklabels=labels, yticklabels=labels, square=True, ax=ax, cbar=False)
    
    ax.set_title("Confusion Matrix", fontsize=13, pad=12)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_residual_plot(y_true, y_pred) -> str:
    """
    Generates residuals plot for regression models using OO API.
    """
    fig = Figure(figsize=(6, 4.5))
    ax = fig.add_subplot(111)
    
    residuals = y_true - y_pred
    sns.scatterplot(x=y_pred, y=residuals, color=COLOR_BLUE, alpha=0.7, ax=ax, edgecolor=BG_COLOR)
    ax.axhline(y=0, color=COLOR_CYAN, linestyle='--', linewidth=1.5)
    
    ax.set_title("Residual Plot", fontsize=13, pad=12)
    ax.set_xlabel("Predicted Values")
    ax.set_ylabel("Residuals (Actual - Predicted)")
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)

def generate_feature_importance_plot(importances: list, col_names: list) -> str:
    """
    Generates feature importance bar plot using OO API.
    """
    fig = Figure(figsize=(7, 4.5))
    ax = fig.add_subplot(111)
    
    idx = np.argsort(importances)[::-1][:15] # Top 15
    sorted_importances = [importances[i] for i in idx]
    sorted_cols = [col_names[i] for i in idx]
    n_items = len(sorted_cols)
    
    sns.barplot(x=sorted_importances, y=sorted_cols, hue=sorted_cols, palette=PALETTE[:n_items], orient='h', ax=ax, legend=False)
    
    ax.set_title("Top Feature Importances", fontsize=14, pad=15)
    ax.set_xlabel("Importance Score")
    apply_dark_theme_to_fig(fig)
    return fig_to_base64(fig)
