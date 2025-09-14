from pydantic import BaseModel
from fastapi import Form

class TicketCreate(BaseModel):
    tanggal: str
    no_tiket: str
    customer: str
    model: str | None = None
    keluhan: str | None = None
    teknisi: str | None = None
    indikasi: str | None = None
    tindakan: str | None = None
    lokasi_koordinat: str | None = None

    @classmethod
    def as_form(
        cls,
        tanggal: str = Form(...),
        no_tiket: str = Form(...),
        customer: str = Form(...),
        model: str = Form(None),
        keluhan: str = Form(None),
        teknisi: str = Form(None),
        indikasi: str = Form(None),
        tindakan: str = Form(None),
        lokasi_koordinat: str = Form(None),
    ):
        return cls(
            tanggal=tanggal,
            no_tiket=no_tiket,
            customer=customer,
            model=model,
            keluhan=keluhan,
            teknisi=teknisi,
            indikasi=indikasi,
            tindakan=tindakan,
            lokasi_koordinat=lokasi_koordinat
        )
