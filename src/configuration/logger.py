import logging
import os
from pathlib import Path


def setup_logging():
    
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    log_dir = os.path.abspath(log_dir)  
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log")),
            logging.FileHandler(os.path.join(log_dir, "error.log")),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
