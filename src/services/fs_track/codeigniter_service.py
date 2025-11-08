# src/services/fs_track/codeigniter_service.py
import aiohttp
from src.models.fs_track.interfaces import IAuthenticator, IJobCreator
from src.models.fs_track.domain_models import Ticket

class CodeIgniterService:
    def __init__(self, authenticator: IAuthenticator, job_creator: IJobCreator):
        self.authenticator = authenticator
        self.job_creator = job_creator
    
    async def create_job_from_ticket(self, ticket: Ticket) -> int:
        # Gunakan aiohttp session instead of requests
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            if not await self.authenticator.login(session):
                raise Exception("Login failed")
            
            return await self.job_creator.create_job(session, ticket)