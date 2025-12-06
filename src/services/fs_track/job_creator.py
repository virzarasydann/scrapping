# src/services/fs_track/job_creator.py
import os

import aiohttp
from aiohttp import FormData

from src.models.fs_track.interfaces import ICSRFHandler, IJobCreator
from src.schemas.fs_track.fs_request_schema import FsRequestSchema as FsTicket
from src.services.fs_track.get_job import GetJob


class JobCreator(IJobCreator):
    def __init__(self, base_url: str, csrf_handler: ICSRFHandler):
        self.base_url = base_url
        self.csrf_handler = csrf_handler

    async def create_job(self, session: aiohttp.ClientSession, ticket: FsTicket) -> int:
        csrf_token = await self.csrf_handler.get_csrf_token(
            session, f"{self.base_url}/admin/jobs/add"
        )

        payload = self._build_payload(ticket, csrf_token)

        async with session.post(
            f"{self.base_url}/admin/jobs/add", data=payload
        ) as response:
            await self._log_request(payload, response)

            if response.status == 200:
                return await self.create_job_detail(session, ticket)

            return response.status

    async def create_job_detail(
        self, session: aiohttp.ClientSession, ticket: FsTicket
    ) -> int:
        get_job = GetJob(self.base_url)
        last_id = await get_job.get_last_job_id(session)

        csrf_token = await self.csrf_handler.get_csrf_token(
            session, f"{self.base_url}/admin/job-details/edit/{last_id}"
        )

        payload = self._payload_jobs_detail(ticket, csrf_token, last_id)

        print(
            f"\n[DEBUG] Mengirim ke URL: {self.base_url}/admin/job-details/edit/{last_id}"
        )
        print(f"[DEBUG] ID Job: {last_id}")
        print(f"[DEBUG] CSRF Token: {csrf_token[:20]}...")

        async with session.post(
            f"{self.base_url}/admin/job-details/edit/{last_id}", data=payload
        ) as response:
            response_text = await response.text()
            print(f"[DEBUG] Response Status: {response.status}")

            return response.status

    def _build_payload(self, ticket: FsTicket, csrf_token: str) -> dict:
        return {
            "csrf_test_name": csrf_token,
            "customer_name": ticket.customer,
            "customer_address": "Jl. Test Integration No.1",
            "customer_phone_number": "081234567890",
            "id_ac_unit": "156",
            "id_service_type": "24",
            "description": f"{ticket.keluhan}\n{ticket.no_ticket}",
            "team": "AhliAC",
            "accessor": "Wahyu Nugraha",
            "start_date": str(ticket.tanggal),
            "end_date": str(ticket.tanggal),
            "save": "1",
        }

    def _payload_jobs_detail(
        self, ticket: FsTicket, csrf_token: str, jobs_id: int
    ) -> FormData:
        form = FormData()

        form.add_field("csrf_test_name", csrf_token)
        form.add_field("id_job_detail", str(jobs_id))
        form.add_field("id_job", str(jobs_id))
        form.add_field("description", f"{ticket.keluhan}\n{ticket.no_ticket}")
        form.add_field("technician_name", "test")
        form.add_field("id_technician", "41")
        form.add_field("job_status", "-")

        base_path = "src/public"
        image_mapping = {
            "before": "image_1",
            "after": "image_2",
            "serial_number": "image_3",
            "lokasi": "image_4",
        }

        for attr, field_name in image_mapping.items():
            file_value = getattr(ticket, attr, None)
            if file_value:
                file_path = os.path.join(base_path, file_value)
                if os.path.exists(file_path):
                    ext = os.path.splitext(file_value)[1].lower()
                    content_type = {
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".png": "image/png",
                        ".gif": "image/gif",
                    }.get(ext, "image/jpeg")

                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        form.add_field(
                            field_name,
                            file_content,
                            filename=os.path.basename(file_value),
                            content_type=content_type,
                        )
                    print(f"[DEBUG] Uploaded {field_name}: {file_value}")
                else:
                    print(f"[WARNING] File not found: {file_path}")

        form.add_field("save", "Save")

        return form

    async def _log_request(self, payload, response: aiohttp.ClientResponse):
        print("\n[DEBUG] Payload yang dikirim:")

        if isinstance(payload, dict):
            for k, v in payload.items():
                print(f"  {k}: {v}")

        elif isinstance(payload, aiohttp.FormData):
            print("  [FormData] multipart/form-data dikirim")

            if hasattr(payload, "_debug_info"):
                for name, value in payload._debug_info.items():
                    print(f"  {name}: {value}")
            else:
                print("  [!] Tidak bisa membaca isi FormData secara detail")
                print("  [!] FormData telah di-encode dan tidak bisa di-inspect")

        else:
            print(f"  [!] Payload bukan dict atau FormData (type={type(payload)})")

        print("[CI] Status:", response.status)
        print("[CI] URL:", response.url)
