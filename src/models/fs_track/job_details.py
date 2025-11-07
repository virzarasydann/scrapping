from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.configuration.database import ClientBase



class JobDetail(ClientBase):
    __tablename__ = 'job_details'

    id_job_detail = Column(Integer, primary_key=True, autoincrement=True)
    id_job = Column(Integer, ForeignKey('jobs.id_jobs'), nullable=False)
    description = Column(Text)
    id_technician = Column(Integer, ForeignKey('technicians.id_technicians'))
    job_status = Column(
        Enum('-', 'Waiting Technician', 'Processing', 'Completed', 'Rescheduled', 'Canceled',
             name='job_status_enum'),
        nullable=False,
        default='-'
    )
    image_1 = Column(Text)
    image_2 = Column(Text)
    image_3 = Column(Text)
    image_4 = Column(Text)
    image_5 = Column(Text)
    image_6 = Column(Text)
    image_7 = Column(Text)
    image_8 = Column(Text)
    image_9 = Column(Text)
    image_10 = Column(Text)
    image_11 = Column(Text)
    image_12 = Column(Text)
    image_13 = Column(Text)
    image_14 = Column(Text)
    image_15 = Column(Text)
    image_16 = Column(Text)
    image_17 = Column(Text)
    image_18 = Column(Text)
    image_19 = Column(Text)
    image_20 = Column(Text)
    created_date = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="job_details")
    technician = relationship("Technician", back_populates="job_details")