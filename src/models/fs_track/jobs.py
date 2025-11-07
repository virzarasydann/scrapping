from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.configuration.database import ClientBase


class Job(ClientBase):
    __tablename__ = 'jobs'

    id_jobs = Column(Integer, primary_key=True, autoincrement=True)
    id_customer = Column(Integer, ForeignKey('customers.id_customer'), nullable=False)
    id_ac_unit = Column(Integer, ForeignKey('ac_units.id_ac_unit'), nullable=False)
    id_service_type = Column(Integer, ForeignKey('service_types.id_service_type'), nullable=False)
    description = Column(Text, nullable=False)
    job_condition = Column(Enum('Start', 'Finish', 'Validated', name='job_condition_enum'))
    team = Column(String(255), nullable=False, default='AhliAC')
    accessor = Column(String(255), nullable=False, default='Wahyu Nugraha')
    start_date = Column(Date)
    end_date = Column(Date)
    created_date = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="jobs")
    ac_unit = relationship("ACUnit", back_populates="jobs")
    service_type = relationship("ServiceType", back_populates="jobs")
    job_details = relationship("JobDetail", back_populates="job")