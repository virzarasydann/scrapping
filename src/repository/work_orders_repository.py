from sqlalchemy.orm import Session
from src.models.work_orders_models import WorkOrder, WorkOrderStatus 

from src.schemas.gree.work_orders_schema import WorkOrderCreate, WorkOrderUpdate 

class WorkOrderRepository:
    
    def create_work_order(self, db: Session, data: WorkOrderCreate):
       
        work_order = WorkOrder(**data.dict())
      

        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        return work_order

    def get_all_work_orders(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(WorkOrder).order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit).all()

    def get_work_order_by_id(self, db: Session, wo_id: int) -> WorkOrder:
        return db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()

    def get_work_order_by_number(self, db: Session, wo_number: str) -> WorkOrder:
        
        return db.query(WorkOrder).filter(WorkOrder.work_order_number == wo_number).first()

    def update_status(self, db: Session, wo_id: int, new_status: WorkOrderStatus):
        
        work_order = self.get_work_order_by_id(db, wo_id)
        if work_order:
            work_order.status = new_status
            db.commit()
            db.refresh(work_order)
            return work_order
        return None

    def update_work_order(self, db: Session, wo_id: int, data: WorkOrderUpdate):
        work_order = self.get_work_order_by_id(db, wo_id)
        if not work_order:
            return None

        
        update_data = data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(work_order, key, value)

        db.commit()
        db.refresh(work_order)
        return work_order

    def delete_work_order(self, db: Session, wo_id: int):
        work_order = self.get_work_order_by_id(db, wo_id)
        if not work_order:
            return False

        db.delete(work_order)
        db.commit()
        return True