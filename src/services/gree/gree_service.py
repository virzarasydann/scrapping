import os
import time
import requests
import shutil
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Tuple, Optional


from src.repository.work_orders_repository import WorkOrderRepository
from src.repository.technician_work_orders_repository import TechnicianWorkOrderRepository
from src.models.message_models import MessageType
from src.schemas.gree.technician_work_orders_schema import MessageResponse as GreeTicket
from src.configuration.config import REMOTE_BASE_URL, LOCAL_TEMP_DIR



class GreeService:
    def __init__(self):
        self.wo_repo = WorkOrderRepository()
        self.assign_repo = TechnicianWorkOrderRepository()
        
       
        if not LOCAL_TEMP_DIR.exists():
            LOCAL_TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self._cleanup_old_files(max_age_minutes=60)


    def _cleanup_old_files(self, max_age_minutes: int = 60):
        """
        Menghapus file di folder temp yang usianya lebih dari X menit.
        Mencegah server penuh jika automation lupa menghapus file.
        """
        try:
            current_time = time.time()
            limit_age = max_age_minutes * 60 

            for file_path in LOCAL_TEMP_DIR.iterdir():
                if file_path.is_file():
                    
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > limit_age:
                        file_path.unlink() 
                        print(f"[AutoCleanup] Deleted old file: {file_path.name}")
        except Exception as e:
            print(f"[AutoCleanup] Error: {e}")


    def _download_file(self, filename: str) -> Optional[str]:
        """
        Helper function untuk download file dari N8N ke folder Temp Lokal.
        Return: Relative Path untuk automation (misal: 'temp/foto.jpg')
        """
        if not filename:
            return None
            
        
        
        remote_url = f"{REMOTE_BASE_URL}/{filename}"
        
       
        clean_filename = os.path.basename(filename) 
        local_file_path = LOCAL_TEMP_DIR / clean_filename
        
        try:
            
            with requests.get(remote_url, stream=True) as r:
                r.raise_for_status() 
                with open(local_file_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            
            
            return f"temp/{clean_filename}"
            
        except Exception as e:
            print(f"Gagal download file {filename}: {str(e)}")
            return None

    def get_work_orders_by_id(
        self, id_work_orders: int, db: Session
    ) -> GreeTicket: 
        
        
        work_order = self.wo_repo.get_work_order_by_id(db, id_work_orders)
        if not work_order:
            raise HTTPException(status_code=404, detail="Work Order not found")

        
        assignments_data = self.assign_repo.get_assignments_by_work_order_id(db, id_work_orders)
        if not assignments_data:
             raise HTTPException(status_code=404, detail="Data teknisi belum tersedia")

       
        raw_indoor = None
        raw_outdoor = None
        raw_lokasi = None
        raw_rumah = None
        
      
        for data in assignments_data:
            messages = data.get("messages", [])
            
            for msg in messages:
               
                content = msg.media_url 

                if msg.jenis_data == MessageType.BARCODE_INDOOR:
                    raw_indoor = content
                elif msg.jenis_data == MessageType.BARCODE_OUTDOOR:
                    raw_outdoor = content
                elif msg.jenis_data == MessageType.FOTO_RUMAH_CUSTOMER:
                    raw_rumah = content
                elif msg.jenis_data == MessageType.SHARE_LOKASI:
                 
                    raw_lokasi = content 

           
            if raw_indoor and raw_outdoor:
                break

       
        
        path_indoor = self._download_file(raw_indoor) if raw_indoor else None
        path_outdoor = self._download_file(raw_outdoor) if raw_outdoor else None
        path_rumah = self._download_file(raw_rumah) if raw_rumah else None
        
        path_lokasi = self._download_file(raw_lokasi) if raw_lokasi else None
       
            
        gree_ticket = GreeTicket(
            work_orders_number=work_order.work_order_number,
            barcode_indoor=path_indoor,      
            barcode_outdoor=path_outdoor,     
            share_lokasi=path_lokasi,
            foto_rumah_customer=path_rumah
            
        )

        return gree_ticket