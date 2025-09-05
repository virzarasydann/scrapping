from src.configuration.database import Base, engine
# from src.models.files_models import File
from src.models.listeners_models import Listener

print("Membuat tabel...")
Base.metadata.create_all(bind=engine)
print("Selesai 🚀")
