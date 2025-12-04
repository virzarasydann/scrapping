import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.configuration.database import get_db
from src.schemas.fs_track.fs_request_schema import FsRequestSchema as FsTicket
from src.services.fs_track.codeigniter_service import CodeIgniterService
from src.services.fs_track.factory import CodeIgniterServiceFactory
from src.services.fs_track_service import FsTrackService
from src.repository.ticket_repository import TicketRepository
router = APIRouter(prefix="/api/v1", tags=["/api/v1"])
logger = logging.getLogger(__name__)


job_status = {}


async def background_create_job(service: CodeIgniterService, ticket, job_id: str, id_ticket):
    """Worker background"""
    db = next(get_db())
    repo: TicketRepository = TicketRepository()
    try:
        job_status[job_id] = {
            "status": "processing",
            "message": "Sedang membuat job di FS Track...",
            "progress": 30,
        }

        result: int = await service.create_job_from_ticket(ticket)
        if result == 500:
            job_status[job_id] = {
                "status": "error",
                "message": "Job gagal",
                "result": result,
                "progress": 0,
            }

            logger.info(f"[BACKGROUND] Job {job_id} gagal, result: {result}")

            return result

        job_status[job_id] = {
            "status": "success",
            "message": "Job berhasil dibuat!",
            "result": result,
            "progress": 100,
        }

        logger.info(f"[BACKGROUND] Job {job_id} selesai, result: {result}")
        repo.set_status_fs(db, id_ticket, 1)
        return result

    except Exception as e:
        job_status[job_id] = {
            "status": "error",
            "message": f"Gagal membuat job: {str(e)}",
            "progress": 0,
        }
        logger.error(f"[BACKGROUND] Job {job_id} error: {str(e)}")
        repo.set_status_fs(db, id_ticket, 0)
        return None
    finally:
        db.close()


@router.get("/create_job")
async def ci_create_job(id_ticket: int, db: Session = Depends(get_db)):
    """Start job creation process"""
    fs_service: FsTrackService = FsTrackService()
    ticket: FsTicket = fs_service.get_ticket_by_id(db, id_ticket)

    job_id = f"job_{id_ticket}_{int(datetime.now().timestamp())}"
    job_status[job_id] = {
        "status": "starting",
        "message": "Memulai proses...",
        "progress": 10,
    }

    service: CodeIgniterService = CodeIgniterServiceFactory.create_service(
        "https://fs.616263.my.id", "ADMIN1", "ADMINAC"
    )

    asyncio.create_task(background_create_job(service, ticket, job_id, id_ticket))

    return {"status": "started", "job_id": job_id, "ticket_id": id_ticket}


@router.get("/job_status/{job_id}")
async def get_job_status(job_id: str):
    """Check job status"""
    if job_id not in job_status:
        raise HTTPException(404, "Job not found")

    status = job_status[job_id]

    if status["status"] in ["success", "error"]:
        pass

    return status
