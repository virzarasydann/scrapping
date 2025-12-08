import logging
from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
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
            error_msg = f"ERROR elemen tidak ditemukan: {description} atau Foto sudah terupload, silahkan dicek kembali"
            raise Exception(error_msg) from e

    def wait_for_element_in_parent(
        self, parent_element, by, value, timeout=5, description="element"
    ):
        """
        Wait for element inside parent element

        Returns:
            WebElement - ALWAYS returns element or raises exception

        Raises:
            TimeoutException - if element not found
        """
        try:
            self.log(f"Mencari {description} di parent element...")

            element = WebDriverWait(parent_element, timeout).until(
                lambda parent: parent.find_element(by, value)
            )

            self.log(f"{description} ditemukan di parent")
            return element  # Always WebElement

        except TimeoutException as e:
            self.log(f"TIMEOUT: {description} tidak ditemukan di parent")
            raise  # Raise exception seperti find_element

        except Exception as e:
            self.log(f"ERROR mencari {description} di parent: {e}")
            raise  # Raise exception seperti find_element
