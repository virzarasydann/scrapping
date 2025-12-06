from datetime import datetime

from src.schemas.gree.gree_request_schema import GreeRequestSchema as GreeTicket
from src.services.gree.gree import Gree



def main():
    print("=== SCRIPT DIMULAI ===")

    ticket = GreeTicket(
        no_ticket="JKA-251206-0002-01",
        customer="John Doe",
        model="AC Deluxe Model X",
        keluhan="Tidak dingin",
        tanggal=datetime.now(),
        before="",
        after="",
        serial_number="btesting.jpg",
        lokasi="btesting.jpg",
        status_gree=0
    )

    gree = Gree(ticket, headless=False)
    gree.run()


if __name__ == "__main__":
    main()
