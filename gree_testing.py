from datetime import datetime

from src.models.fs_track.domain_models import Ticket
from src.services.gree.gree import Gree


def main():
    print("=== SCRIPT DIMULAI ===")

    ticket = Ticket(
        no_ticket="JKB-251129-0012-01",
        customer="John Doe",
        model="AC Deluxe Model X",
        keluhan="Tidak dingin",
        tanggal=datetime.now(),
        before="",
        after="",
        serial_number="f9557080310f402dbf86700031920cb7.jpg",
        lokasi="Jakarta",
    )

    gree = Gree(ticket, headless=False)
    gree.run()


if __name__ == "__main__":
    main()
