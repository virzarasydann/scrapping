# src/services/fs_track/authenticator.py
import aiohttp
from src.models.fs_track.interfaces import IAuthenticator, ICSRFHandler
from src.models.fs_track.domain_models import LoginCredentials

class CodeIgniterAuthenticator(IAuthenticator):
    def __init__(self, base_url: str, credentials: LoginCredentials, csrf_handler: ICSRFHandler):
        self.base_url = base_url
        self.credentials = credentials
        self.csrf_handler = csrf_handler
    
    async def login(self, session: aiohttp.ClientSession) -> bool:
        csrf_token = await self.csrf_handler.get_csrf_token(session, f"{self.base_url}/login")
        
        login_payload = {
            "login": self.credentials.username,
            "password": self.credentials.password,
            "csrf_test_name": csrf_token
        }
        
        async with session.post(f"{self.base_url}/login", data=login_payload) as response:
            return "login" not in str(response.url)