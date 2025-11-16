from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.services.sector_service import fetch_sector_data
import pandas as pd
import io

def generate_pdf_report(sector: str, portfolio_harm_scores: dict) -> bytes:
    """Generate PDF report for a sector"""
    buffer = io.BytesIO()
    
    # Use landscape orientation
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    # Add styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Create custom style for table cells
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=5,
        leading=6,
        wordWrap='CJK'
    )
    
    # Add title
    elements.append(Paragraph("Corporate Racial Equity Intelligence Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Add sector info
    elements.append(Paragraph(f"Sector: {sector}", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Add portfolio metrics
    elements.append(Paragraph("Portfolio Racial Equity Summary", subtitle_style))
    
    portfolio_data = [
        ["Metric", "Value"],
        ["Average Portfolio Equity Score", f"{portfolio_harm_scores['average_score']:.1f}"],
        ["Total Portfolio Equity Score", f"{int(portfolio_harm_scores['total_score']):,}"],
        ["Total Portfolio Equity Quartile", f"{portfolio_harm_scores['quartile']}"]
    ]
    
    portfolio_table = Table(portfolio_data, colWidths=[300, 200])
    portfolio_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(portfolio_table)
    elements.append(Spacer(1, 16))
    
    # Add sector harm profile table
    elements.append(Paragraph(f"Detailed {sector} Sector Equity Profile", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Fetch sector data
    df = fetch_sector_data(sector)
    if not df.empty:
        profile_df = df[['SDH_Indicator', 'SDH_Category', 'Harm_Description', 'Harm_Typology', 
                       'Claim_Quantification', 'Total_Magnitude', 'Reach', 'Harm_Direction', 
                       'Harm_Duration', 'Total_Score', 'Direct_Indirect', 'Direct_Indirect_1',
                       'Core_Peripheral', 'Citation_1', 'Citation_2']]
        
        # Rename columns
        profile_df = profile_df.rename(columns={
            'SDH_Indicator': 'SDH Indicator',
            'SDH_Category': 'SDH Category',
            'Harm_Description': 'Equity Description',
            'Harm_Typology': 'Equity Typology',
            'Claim_Quantification': 'Claim Quantification',
            'Total_Magnitude': 'Total Magnitude',
            'Harm_Direction': 'Equity Direction',
            'Harm_Duration': 'Equity Duration',
            'Total_Score': 'Total Score'
        })
        
        # Convert to table data
        header_row = [Paragraph(f"<b>{col}</b>", cell_style) for col in profile_df.columns]
        table_data = [header_row]
        
        for _, row in profile_df.iterrows():
            table_row = [Paragraph(str(value), cell_style) for value in row.values]
            table_data.append(table_row)
        
        harm_table = Table(
            table_data,
            colWidths=[35, 35, 60, 35, 45, 30, 30, 35, 35, 30, 40, 40, 40, 30, 30],
            repeatRows=1
        )
        
        harm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.black)
        ]))
        
        elements.append(harm_table)
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

