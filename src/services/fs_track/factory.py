from src.models.fs_track.domain_models import LoginCredentials
from src.services.fs_track.authenticator import CodeIgniterAuthenticator
from src.services.fs_track.csrf_handler import CSRFHandler
from src.services.fs_track.job_creator import JobCreator
from src.services.fs_track.codeigniter_service import CodeIgniterService

class CodeIgniterServiceFactory:
    @staticmethod
    def create_service(
        base_url: str, 
        username: str, 
        password: str
    ) -> CodeIgniterService:
        
        credentials = LoginCredentials(username=username, password=password)
        
        csrf_handler = CSRFHandler()
        authenticator = CodeIgniterAuthenticator(base_url, credentials, csrf_handler)
        
        job_creator = JobCreator(base_url, csrf_handler)
        
        return CodeIgniterService(authenticator, job_creator)