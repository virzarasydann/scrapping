# src/services/fs_track/csrf_handler.py
import aiohttp
from bs4 import BeautifulSoup
from src.models.fs_track.interfaces import ICSRFHandler

class CSRFHandler(ICSRFHandler):
    async def get_csrf_token(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            csrf_meta = soup.find("meta", {"name": "csrf_test_name"})
            
            if not csrf_meta:
                raise ValueError("CSRF token not found")
            
            return csrf_meta["content"]