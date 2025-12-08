
from sqlalchemy import Column, Integer, String, Date, Text, DateTime
from sqlalchemy.sql import func
from src.configuration.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer, nullable=False)
    tanggal = Column(Date, nullable=False)                            
    no_tiket = Column(String(64), unique=True, nullable=False, index=True)       
    customer = Column(String(255), nullable=True)                    
    model = Column(String(255), nullable=True)                       
    keluhan = Column(Text, nullable=True)                            
    teknisi = Column(String(255), nullable=True)                      
    indikasi = Column(String(255), nullable=True)                     
    tindakan = Column(String(255), nullable=True)                     

        
    before = Column(String(512), nullable=True)                       
    after = Column(String(512), nullable=True)                        
    serial_number_indoor = Column(String(255), nullable=False)       
    serial_number_outdoor = Column(String(255), nullable=False)        
    lokasi = Column(String(255), nullable=False)
    route_navigation = Column(String(255), nullable=False)
    lokasi_koordinat = Column(String(255), nullable=True)            
    status_fs = Column(Integer, nullable=True)
    status_gree = Column(Integer, nullable=True)

    
