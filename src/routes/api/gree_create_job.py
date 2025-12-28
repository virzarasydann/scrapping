import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.configuration.database import get_db
from src.services.gree.gree import Gree
from src.services.gree.gree_service import GreeService

router = APIRouter(prefix="/api/v1", tags=["/api/v1"])
logger = logging.getLogger(__name__)


job_status = {}


def update_job_status(
    id_work_orders: int, status: str, message: str, progress: int, current_step: str
):
    """Helper function untuk update status job"""
    job_status[id_work_orders] = {
        "status": status,
        "message": message,
        "progress": progress,
        "current_step": current_step,
        "timestamp": datetime.now().isoformat(),
    }


def process_gree_job(id_work_orders: int, db: Session):
    """Background task untuk menjalankan Gree automation"""
    try:
        update_job_status(
            id_work_orders, "processing", "Memulai proses automation", 0, "Inisialisasi"
        )

        gree_service = GreeService()
        gree_ticket = gree_service.get_work_orders_by_id(id_work_orders, db)

        update_job_status(
            id_work_orders, "processing", "Membuat instance Gree", 10, "Setup Browser"
        )

        gree = Gree(gree_ticket, headless=True)

        def status_callback(step: str, progress: int):
            update_job_status(
                id_work_orders, "processing", f"Menjalankan: {step}", progress, step
            )

        gree.status_callback = status_callback

        update_job_status(
            id_work_orders, "processing", "Menjalankan automation", 20, "Memulai run()"
        )

        gree.run()

        update_job_status(
            id_work_orders,
            "completed",
            "Proses automation berhasil diselesaikan",
            100,
            "Selesai",
        )

        logger.info(f"Job {id_work_orders} completed successfully")
       

    except Exception as e:
        current_progress = job_status.get(id_work_orders, {}).get("progress", 0)
        job_status[id_work_orders] = {
            "status": "failed",
            "message": f"Error: {str(e)}",
            "progress": current_progress,
            "current_step": "Error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
        logger.error(f"Job {id_work_orders} failed: {str(e)}")
    finally:
        try:
            if "gree" in locals():
                gree.driver.quit()
        except:
            pass


@router.post("/gree_create_job")
async def gree_create_job(
    id_work_orders: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Endpoint untuk memulai job automation GREE di background

    Returns:
        - job_id: ID ticket yang diproses
        - status: Status awal job
        - message: Pesan informasi
    """
    try:
        if id_work_orders in job_status and job_status[id_work_orders]["status"] == "processing":
            return JSONResponse(
                status_code=409,
                content={
                    "job_id": id_work_orders,
                    "status": "already_running",
                    "message": "Job untuk ticket ini sedang berjalan",
                    "current_progress": job_status[id_work_orders],
                },
            )

        update_job_status(id_work_orders, "queued", "Job telah diantrekan", 0, "Menunggu")

        background_tasks.add_task(process_gree_job, id_work_orders, db)

        return JSONResponse(
            status_code=202,
            content={
                "job_id": id_work_orders,
                "status": "queued",
                "message": "Job telah dimulai di background. Gunakan endpoint /gree_job_status untuk memonitor progress",
                "status_endpoint": f"/api/v1/gree_job_status?id_work_orders={id_work_orders}",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gree_job_status")
async def get_job_status(id_work_orders: int):
    """
    Endpoint untuk memeriksa status job

    Returns:
        - status: queued, processing, completed, failed
        - message: Pesan status
        - progress: 0-100
        - current_step: Langkah yang sedang dijalankan
    """
    if id_work_orders not in job_status:
        raise HTTPException(
            status_code=404,
            detail="Job tidak ditemukan. Mungkin belum pernah dijalankan atau sudah dihapus.",
        )

    return JSONResponse(content=job_status[id_work_orders])


@router.delete("/gree_job_status")
async def clear_job_status(id_work_orders: int):
    """
    Endpoint untuk menghapus status job dari memory
    (Berguna untuk cleanup setelah job selesai)
    """
    if id_work_orders in job_status:
        del job_status[id_work_orders]
        return JSONResponse(
            content={"message": f"Status job {id_work_orders} berhasil dihapus"}
        )

    raise HTTPException(status_code=404, detail="Job tidak ditemukan")


@router.get("/gree-work_order")
async def get_gree_work_worder(id_work_orders: int, db: Session = Depends(get_db)):
    gree_service = GreeService()
    gree_ticket = gree_service.get_work_orders_by_id(id_work_orders, db)

    return gree_ticket

