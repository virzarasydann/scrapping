import aiohttp
from typing import Optional
from src.models.fs_track.interfaces import IGetJob

class GetJob(IGetJob):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_last_job(self, session: aiohttp.ClientSession):
        async with session.get(f"{self.base_url}/admin/jobs/json") as response:
            data = await response.json()
            return data

    async def get_last_job_id(self, session: aiohttp.ClientSession) -> Optional[int]:
        async with session.get(f"{self.base_url}/admin/jobs/json") as response:
            data = await response.json()
            
          

            jobs = data.get("data", [])
            if not jobs:
                return None

            
            last_job = jobs[-1]

            return last_job.get("id_jobs")

    async def _log_request(self, response: aiohttp.ClientResponse):
        print("[CI] Status:", response.status)
        print("[CI] URL:", response.url)
