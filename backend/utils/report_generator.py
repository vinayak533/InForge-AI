import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Color Palette matching InForge AI Design
BG_DARK = colors.HexColor('#080B14')
CARD_BG = colors.HexColor('#0E1320')
BORDER_COLOR = colors.HexColor('#1C2333')
TEXT_PRIMARY = colors.HexColor('#F0F4FF')
TEXT_SECONDARY = colors.HexColor('#8B9CC8')
ACCENT_CYAN = colors.HexColor('#00D4FF')
ACCENT_BLUE = colors.HexColor('#0080FF')
COLOR_WHITE = colors.HexColor('#FFFFFF')

def generate_pdf_report(session_id: str, context: dict) -> bytes:
    """
    Generates a professional PDF analysis report using the InForge AI shared context structure.
    Returns the compiled PDF as bytes.
    """
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    style_title = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=26,
        textColor=ACCENT_CYAN,
        spaceAfter=6,
        alignment=0
    )
    
    style_subtitle = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=TEXT_SECONDARY,
        spaceAfter=25,
        alignment=0
    )
    
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=ACCENT_CYAN,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=ACCENT_BLUE,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        spaceAfter=8,
        leading=14
    )
    
    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    style_meta_label = ParagraphStyle(
        'MetaLabel',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=TEXT_SECONDARY
    )
    
    style_meta_val = ParagraphStyle(
        'MetaVal',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_PRIMARY
    )

    story = []
    
    # Header block/Title
    story.append(Paragraph("INFORGE AI", style_title))
    story.append(Paragraph(f"Data Intelligence Report  |  Session ID: {session_id}", style_subtitle))
    
    # Summary of Ingestion
    row_count = context.get('row_count', 'N/A')
    col_count = context.get('column_count', 'N/A')
    target_col = context.get('potential_target', 'N/A')
    
    story.append(Paragraph("1. Executive Summary", style_h1))
    
    # Executive Summary Paragraph
    exec_summary = context.get('insights_agent', {}).get('executive_summary', 
                   "This automated analytics pipeline executed a comprehensive assessment of the uploaded dataset. Ingestion, cleaning, exploratory distribution analysis, and predictive modeling have been successfully performed.")
    story.append(Paragraph(exec_summary, style_body))
    story.append(Spacer(1, 10))
    
    # Dataset KPI Table
    kpi_data = [
        [Paragraph("Rows Detected", style_meta_label), Paragraph(f"{row_count:,}" if isinstance(row_count, int) else row_count, style_meta_val),
         Paragraph("Columns Detected", style_meta_label), Paragraph(f"{col_count:,}" if isinstance(col_count, int) else col_count, style_meta_val)],
        [Paragraph("Missing Value %", style_meta_label), Paragraph(f"{context.get('cleaning_agent', {}).get('null_counts', {}).get('total', 0):,}", style_meta_val),
         Paragraph("Duplicates Removed", style_meta_label), Paragraph(f"{context.get('cleaning_agent', {}).get('duplicate_count', 0):,}", style_meta_val)],
        [Paragraph("Target Feature", style_meta_label), Paragraph(str(target_col), style_meta_val),
         Paragraph("Best Model Found", style_meta_label), Paragraph(str(context.get('ml_agent', {}).get('best_model', 'N/A')), style_meta_val)]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # Business Insights
    insights = context.get('insights_agent', {}).get('insights', [])
    if insights:
        story.append(Paragraph("2. Strategic Insights", style_h1))
        for ins in insights:
            story.append(Paragraph(f"&bull; <b>Insight:</b> {ins}", style_bullet))
        story.append(Spacer(1, 15))
        
    recommendations = context.get('insights_agent', {}).get('recommendations', [])
    if recommendations:
        story.append(Paragraph("3. Recommendations", style_h1))
        for rec in recommendations:
            story.append(Paragraph(f"&bull; {rec}", style_bullet))
        story.append(Spacer(1, 15))

    # Page Break for Visualizations & ML
    story.append(PageBreak())
    
    story.append(Paragraph("4. Analytical Visualizations", style_h1))
    
    # Grab generated charts from visual agent
    vis_data = context.get('visualization_agent', {})
    charts = vis_data.get('charts', {})
    
    # If we have base64 charts, add them to PDF
    added_charts = 0
    for chart_name, chart_b64 in charts.items():
        if added_charts >= 4:  # limit to top 4 in report to keep compact
            break
        try:
            # Decode b64
            img_data = base64.b64decode(chart_b64)
            img_io = io.BytesIO(img_data)
            img_flowable = Image(img_io, width=5.5*inch, height=3.2*inch)
            story.append(KeepTogether([
                Paragraph(f"Figure: {chart_name.replace('_', ' ').title()}", style_h2),
                Spacer(1, 4),
                img_flowable,
                Spacer(1, 15)
            ]))
            added_charts += 1
        except Exception as e:
            continue
            
    # Page Break for Machine Learning
    ml_data = context.get('ml_agent', {})
    if ml_data and ml_data.get('model_results'):
        story.append(PageBreak())
        story.append(Paragraph("5. Predictive Modeling & Evaluation", style_h1))
        story.append(Paragraph(f"The automated machine learning system identified the task as a <b>{ml_data.get('task_type', 'predictive').upper()}</b> problem. Let's compare all tested models and review their metrics:", style_body))
        story.append(Spacer(1, 10))
        
        # Model Comparison Table
        results = ml_data.get('model_results', [])
        if results:
            # Table headers
            headers = list(results[0].keys())
            table_data = [[Paragraph(f"<b>{h.replace('_', ' ').upper()}</b>", style_meta_label) for h in headers]]
            
            for row in results:
                row_cells = []
                for k, v in row.items():
                    if isinstance(v, float):
                        val_str = f"{v:.4f}"
                    else:
                        val_str = str(v)
                    row_cells.append(Paragraph(val_str, style_meta_val))
                table_data.append(row_cells)
                
            num_cols = len(headers)
            col_widths = [1.8*inch] + [1.2*inch] * (num_cols - 1)
            ml_table = Table(table_data, colWidths=col_widths)
            ml_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), CARD_BG),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
                ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ]))
            story.append(ml_table)
            story.append(Spacer(1, 15))
            
        best_model = ml_data.get('best_model', 'N/A')
        best_score = ml_data.get('best_score', 'N/A')
        if best_score != 'N/A' and isinstance(best_score, float):
            best_score_str = f"{best_score:.4f}"
        else:
            best_score_str = str(best_score)
            
        story.append(Paragraph(f"<b>Conclusion:</b> the best performing model is <b>{best_model}</b> with a score of <b>{best_score_str}</b>.", style_body))
        
        # If we have ML visual plots (SHAP, residual or confusion matrix)
        ml_plots = ml_data.get('plots', {})
        if ml_plots:
            for plot_name, plot_b64 in ml_plots.items():
                try:
                    img_data = base64.b64decode(plot_b64)
                    img_io = io.BytesIO(img_data)
                    img_flowable = Image(img_io, width=4.5*inch, height=3.0*inch)
                    story.append(KeepTogether([
                        Spacer(1, 10),
                        Paragraph(f"Model Feature / Error Assessment: {plot_name.replace('_', ' ').title()}", style_h2),
                        Spacer(1, 4),
                        img_flowable
                    ]))
                except Exception as e:
                    continue

    # Document decorator for dark background and pagination
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(TEXT_SECONDARY)
        canvas.drawRightString(doc.pagesize[0] - 40, 20, f"Page {doc.page}  |  Generated by InForge AI")
        canvas.restoreState()

    # Build PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
