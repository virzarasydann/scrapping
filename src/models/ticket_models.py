
from sqlalchemy import Column, Integer, String, Date, Text, DateTime
from sqlalchemy.sql import func
from src.configuration.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer, nullable=False)
    tanggal = Column(Date, nullable=False)                            
    no_tiket = Column(String(64), unique=True, nullable=False, index=True)       
    customer = Column(String(255), nullable=False)                    
    model = Column(String(255), nullable=True)                       
    keluhan = Column(Text, nullable=True)                            
    teknisi = Column(String(255), nullable=True)                      
    indikasi = Column(String(255), nullable=True)                     
    tindakan = Column(String(255), nullable=True)                     

        
    before = Column(String(512), nullable=True)                       
    after = Column(String(512), nullable=True)                        
    serial_number = Column(String(255), nullable=True)                
    lokasi = Column(String(255), nullable=True)
    lokasi_koordinat = Column(String(255), nullable=True)                        

    
