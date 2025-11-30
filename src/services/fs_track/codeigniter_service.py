# src/services/fs_track/codeigniter_service.py
import aiohttp

from src.models.fs_track.domain_models import Ticket
from src.services.fs_track.job_creator import JobCreator
from src.services.fs_track.authenticator import CodeIgniterAuthenticator
class CodeIgniterService:
    def __init__(self, authenticator: CodeIgniterAuthenticator, job_creator: JobCreator):
        self.authenticator = authenticator
        self.job_creator = job_creator
    
    async def create_job_from_ticket(self, ticket: Ticket) -> int:
        # Gunakan aiohttp session instead of requests
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            if not await self.authenticator.login(session):
                raise Exception("Login failed")
            
            return await self.job_creator.create_job(session, ticket)