from fastapi import Form
from pydantic import BaseModel, field_validator
from typing import Optional

class TicketCreate(BaseModel):
    tanggal: str
    no_tiket: str
    customer: str
    model: Optional[str] = None
    keluhan: Optional[str] = None
    teknisi: Optional[str] = None
    indikasi: Optional[str] = None
    tindakan: Optional[str] = None
    lokasi_koordinat: Optional[str] = None

    @field_validator("tanggal", "no_tiket", "customer")
    def required_not_empty(cls, v, field):
        if v is None or str(v).strip() == "":
            raise ValueError(f"{field.field_name} tidak boleh kosong")
        return v


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
