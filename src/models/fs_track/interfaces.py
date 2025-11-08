from abc import ABC, abstractmethod
import requests
from src.models.fs_track.domain_models import Ticket

class ICSRFHandler(ABC):
    @abstractmethod
    def get_csrf_token(self, session: requests.Session, url: str) -> str:
        pass

class IAuthenticator(ABC):
    @abstractmethod
    def login(self, session: requests.Session) -> bool:
        pass

class IJobCreator(ABC):
    @abstractmethod
    def create_job(self, session: requests.Session, ticket: Ticket) -> int:
        pass

class IGetJob(ABC):
    @abstractmethod
    def get_last_job(self, session: requests.Session) -> list:
        pass

    @abstractmethod
    def get_last_job_id(self, session: requests.Session) -> list:
        pass

