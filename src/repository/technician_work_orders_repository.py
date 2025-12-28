from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, cast, Date


from src.models.technician_work_orders_models import TechnicianWorkOrder
from src.models.message_models import Message
from src.models.work_orders_models import WorkOrder
from src.models.technician_models import Technician 

class TechnicianWorkOrderRepository:

    def get_assignment_by_id(self, db: Session, assignment_id: int):
        
        """
        Mengambil 1 data penugasan spesifik berdasarkan ID tabel pivot.
        Berguna untuk detail view atau sebelum delete/update.
        """
        return db.query(TechnicianWorkOrder)\
            .options(joinedload(TechnicianWorkOrder.profile_technician))\
            .options(joinedload(TechnicianWorkOrder.work_order))\
            .filter(TechnicianWorkOrder.id == assignment_id)\
            .first()

    def get_assignments_by_work_order_id(self, db: Session, wo_id: int):
    
        """
        Mengambil daftar teknisi yang mengerjakan WO tertentu (wo_id).
        DAN mengambil pesan/foto yang dikirim oleh teknisi tersebut
        sesuai dengan tanggal SPK Work Order.
        """
        
       
        assignments = db.query(TechnicianWorkOrder)\
            .join(WorkOrder, TechnicianWorkOrder.work_order_id == WorkOrder.id)\
            .join(Technician, TechnicianWorkOrder.technician_id == Technician.id)\
            .options(joinedload(TechnicianWorkOrder.work_order))\
            .options(joinedload(TechnicianWorkOrder.profile_technician))\
            .filter(TechnicianWorkOrder.work_order_id == wo_id)\
            .all()

        results = []

       
        for task in assignments:
            print(f"Ini Task {task}")
            wo = task.work_order
            print(f"Ini Work Order {wo}")
            tech = task.profile_technician 
            print(f"Ini tech {tech}")
            
            filters = [
                Message.work_order_id == wo.id,
                Message.nomor_pengirim == tech.phone_number
            ]
            
            if wo.spk_date:
                filters.append(cast(Message.created_at, Date) == wo.spk_date)

            relevant_messages = db.query(Message).filter(and_(*filters)).all()

            final_messages = relevant_messages if relevant_messages else []
           

            
            results.append({
                "assignment_id": task.id,
                
                "technician": {
                    "id": tech.id,
                    "name": tech.name,
                    "phone_number": tech.phone_number,
                    "level": tech.level
                },
                
                "messages": final_messages,
                
                
                "assigned_at": task.created_at
            })

        return results

    def get_technician_report(self, db: Session, technician_id: int, filter_date: str = None):
        """
        Mengambil daftar Work Order milik teknisi tertentu,
        Lalu memfilter pesan di dalamnya yang HANYA dikirim oleh nomor HP teknisi tersebut
        dan sesuai dengan tanggal SPK (atau filter_date).
        """
        
        
        query = db.query(TechnicianWorkOrder)\
            .join(WorkOrder, TechnicianWorkOrder.work_order_id == WorkOrder.id)\
            .join(Technician, TechnicianWorkOrder.technician_id == Technician.id)\
            .options(joinedload(TechnicianWorkOrder.work_order))\
            .options(joinedload(TechnicianWorkOrder.profile_technician))\
            .filter(TechnicianWorkOrder.technician_id == technician_id)

        
        if filter_date:
            query = query.filter(WorkOrder.spk_date == filter_date)

        assignments = query.all()
        
        results = []

        
        for task in assignments:
            wo = task.work_order
            tech = task.profile_technician
            
           
            
            target_date = wo.spk_date
            if filter_date:
                target_date = filter_date 

            relevant_messages = db.query(Message).filter(
                and_(
                    Message.work_order_id == wo.id,
                    Message.nomor_pengirim == tech.phone_number,
                    cast(Message.created_at, Date) == target_date
                )
            ).all()

            
            results.append({
                "assignment_id": task.id,
                "work_order": {
                    "id": wo.id,
                    "wo_number": wo.work_order_number,
                    "customer_name": wo.customer_name,
                    "spk_date": wo.spk_date,
                    "address": wo.address
                },
                "technician": {
                    "id": tech.id,
                    "name": tech.name,
                    "phone_number": tech.phone_number
                },
               
                "technician_messages": relevant_messages 
            })

        return results