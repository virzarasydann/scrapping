from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from src.services.webhook_services import WebhookService
from src.configuration.database import get_db
import logging
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def webhook_post(
    request: Request, 
    db: Session = Depends(get_db)
):
    try:
        body = await request.json()
        logger.info(f"Received POST payload: {body}")
        
        service = WebhookService(db)
        result = await service.process_webhook(body)
        
        return result
        
    except Exception as e:
        logger.exception("Unexpected error in webhook endpoint")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )