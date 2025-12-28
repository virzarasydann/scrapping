from src.configuration.database import SessionLocal
from src.services.gree.gree import Gree
from src.services.gree.gree_service import GreeService


def main():
    print("=== SCRIPT DIMULAI ===")
    db = SessionLocal()
    try:
        service = GreeService()
        gree_ticket = service.get_work_orders_by_id(93, db)

        gree = Gree(gree_ticket, headless=False)
        gree.run()

    finally:
        db.close()


if __name__ == "__main__":
    main()
