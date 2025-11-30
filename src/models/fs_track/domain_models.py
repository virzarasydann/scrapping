from dataclasses import dataclass
from datetime import datetime

@dataclass
class Ticket:
    no_ticket: str
    customer: str
    model: str
    keluhan: str
    tanggal: datetime
    before: str
    after: str
    serial_number: str
    lokasi: str
    status_gree: int

@dataclass
class LoginCredentials:
    username: str
    password: str

@dataclass
class JobCreationResult:
    success: bool
    status_code: int
    message: str = ""