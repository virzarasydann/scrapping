import logging
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from src.configuration.config import SRC_DIR

logger = logging.getLogger(__name__)


def setup_static_files(app):
    """Setup static files secara otomatis"""

    templates_static_dir = SRC_DIR / "templates" / "static"
    public_dir = SRC_DIR / "public"

    app.mount("/static", StaticFiles(directory=templates_static_dir), name="static")
    app.mount("/public", StaticFiles(directory=public_dir), name="public")
