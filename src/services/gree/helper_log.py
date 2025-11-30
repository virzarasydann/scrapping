import logging
from typing import TYPE_CHECKING

from selenium.webdriver.support.ui import WebDriverWait

from src.configuration.logger import setup_logging


if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver

logger = logging.getLogger(__name__)
setup_logging()

class SeleniumHelper:
    driver: "WebDriver"
    wait: WebDriverWait

    def log(self, message):
        logger.info(f"[GREE] {message}")

    def wait_for(self, description: str, condition):
        try:
            self.log(f"Menunggu elemen: {description}")
            element = self.wait.until(condition)
            self.log(f"Elemen ditemukan: {description}")
            return element
        except Exception as e:
            self.log(f"ERROR elemen tidak ditemukan: {description} | {e}")
            raise
