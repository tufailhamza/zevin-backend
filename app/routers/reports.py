from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import ReportRequest
from app.services import report_service
import io

router = APIRouter()

@router.post("/pdf")
async def generate_report(report_request: ReportRequest):
    """Generate PDF report for a sector"""
    try:
        pdf_buffer = report_service.generate_pdf_report(
            sector=report_request.sector,
            portfolio_harm_scores=report_request.portfolio_harm_scores.model_dump()
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=racial_equity_report_{report_request.sector}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

