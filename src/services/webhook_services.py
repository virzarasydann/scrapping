
import aiohttp
import aiofiles
import uuid
import os
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.listeners_models import Listener
from src.models.files_models import File
from pathlib import Path
import logging
from src.configuration.config import PUBLIC_DIR

logger = logging.getLogger(__name__)



class WebhookService:
    def __init__(self, db: Session):
        self.db = db

    async def process_webhook(self, body: dict) -> dict:
        file_url = body.get("url", "").strip()
        extension = body.get("extension", "").strip()
        nama = body.get("name", "").strip()
        message = body.get("message", "").strip()
        nomer = body.get("pengirim", "").strip()
        lokasi = body.get("location", "").strip()

        # Handle #LAPOR command
        if "#LAPOR" in message.upper():
            return await self._activate_listener(nomer)
        
        # Handle #SELESAI command
        if "#SELESAI" in message.upper():
            return await self._deactivate_listener(nomer)
        
        # Process regular message
        listener = self._get_active_listener(nomer)
        if not listener:
            return {"message": "Listener tidak aktif, pesan diabaikan."}
        
        return await self._process_message(
            file_url, extension, nama, message, nomer, lokasi
        )

    async def _activate_listener(self, nomer: str) -> dict:
        listener = self.db.query(Listener).filter(Listener.nomer == nomer).first()
        if listener:
            listener.aktif = True
            listener.started_at = datetime.now()
            listener.ended_at = None
            logger.info(f"Listener diaktifkan kembali untuk nomor {nomer}")
        else:
            listener = Listener(nomer=nomer, aktif=True, nama=nama)
            self.db.add(listener)
            logger.info(f"Listener baru dibuat untuk nomor {nomer}")
        
        self.db.commit()
        return {"message": f"Listener aktif untuk {nomer}"}

    async def _deactivate_listener(self, nomer: str) -> dict:
        listener = self.db.query(Listener).filter(
            Listener.nomer == nomer, 
            Listener.aktif == True
        ).first()
        
        if listener:
            listener.aktif = False
            listener.ended_at = datetime.now()
            self.db.commit()
            logger.info(f"Listener dinonaktifkan untuk nomor {nomer}")
            return {"message": f"Listener dimatikan untuk {nomer}"}
        else:
            logger.info(f"Tidak ada listener aktif untuk {nomer} yang bisa dimatikan")
            return {"message": f"Tidak ada listener aktif untuk {nomer}"}

    def _get_active_listener(self, nomer: str) -> Listener:
        return self.db.query(Listener).filter(
            Listener.nomer == nomer, 
            Listener.aktif == True
        ).first()

    async def _process_message(self, file_url, extension, nama, message, nomer, lokasi) -> dict:
        cleaned_message = message.strip()

        if not ((file_url and extension) or lokasi or cleaned_message):
            logger.info("Tidak ada file, lokasi, atau pesan yang valid")
            return {"message": "Tidak ada data valid, skip database."}

        filename, filepath = None, None
        
        if file_url and extension:
            filename, filepath = await self._download_file(file_url, extension)

        try:
            new_file = File(
                nomer=nomer,
                nama=nama,
                message=cleaned_message,
                url=file_url if file_url else None,
                extension=extension if extension else None,
                filename=filename,
                location=lokasi if lokasi else None,
            )
            self.db.add(new_file)
            self.db.commit()
            self.db.refresh(new_file)

            logger.info(f"Data tersimpan, ID: {new_file.id}")
            return {
                "message": "Pesan disimpan (listener aktif)",
                "saved_file": filepath,
                "db_id": new_file.id
            }

        except Exception as e:
            logger.exception("Error saat simpan DB")
            raise e

    async def _download_file(self, file_url: str, extension: str) -> tuple:
        filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join(PUBLIC_DIR, filename)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status != 200:
                        logger.error(f"Gagal download file: {file_url}, status={resp.status}")
                        return None, None
                    data = await resp.read()
                    async with aiofiles.open(filepath, "wb") as f:
                        await f.write(data)
            
            logger.info(f"File berhasil disimpan: {filepath}")
            return filename, filepath
        except Exception:
            logger.exception("Error saat download file")
            return None, None