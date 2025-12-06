# services/gree.py
import os
import random
import time
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.configuration.config import (
    GREE_COOKIE_TEMP,
    GREE_HOME_URL,
    GREE_LOGIN_URL,
    LOCATORS,
    PUBLIC_DIR,
)
from src.schemas.gree.gree_request_schema import GreeRequestSchema as GreeTicket
from src.services.gree.helper_log import SeleniumHelper


def rdelay(a=0.5, b=1.5):
    """Delay random antara a - b detik."""
    time.sleep(random.uniform(a, b))


class Gree(SeleniumHelper):
    def __init__(self, ticket: GreeTicket, headless: bool = True):
        options = Options()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.ticket = ticket
        self.status_callback = None

    def _update_status(self, step: str, progress: int):
        """Internal method untuk update status via callback"""
        if self.status_callback:
            self.status_callback(step, progress)

    def get_login_url(self):
        """Menuju ke link dari GREE_LOGIN_URL"""

        self.driver.get(url=GREE_LOGIN_URL)

    def get_home_url(self):
        """Function ini digunakan setelah login berhasil"""

        self.driver.get(url=f"{GREE_HOME_URL}")

    def fill_no_work_order(self, workorder_code: GreeTicket):
        """
        Hal pertama yang dilakukan adalah mencari elemen dari input no_work_order
        """

        no_wo_input = self.wait_for(
            "Input No Work Order",
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, LOCATORS["input_no_work_order"])
            ),
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", no_wo_input
        )
        rdelay(0.8, 1.2)

        self.driver.execute_script("arguments[0].focus();", no_wo_input)
        self.driver.execute_script("arguments[0].value = '';", no_wo_input)
        rdelay(0.3, 0.6)

        """
        Bagian ini akan mengetik huruf satu persatu dari no_ticket
        """
        for char in workorder_code.no_ticket:
            no_wo_input.send_keys(char)
            rdelay(0.05, 0.15)

        cari_button = self.wait_for(
            description="Cari Button",
            condition=EC.element_to_be_clickable(
                (
                    By.XPATH,
                    LOCATORS["button_cari"],
                )
            ),
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", cari_button
        )
        rdelay(0.5, 1.0)

        try:
            cari_button.click()
        except:
            self.driver.execute_script("arguments[0].click();", cari_button)

        rdelay(2, 3)

    def click_edit_icon(self):
        try:
            edit_icon = self.wait_for(
                description="Click icon edit",
                condition=EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        LOCATORS["icon_edit"],
                    )
                ),
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", edit_icon
            )
            rdelay(0.5, 1.0)

            try:
                edit_icon.click()
            except:
                self.driver.execute_script("arguments[0].click();", edit_icon)

            rdelay(1, 2)

        except Exception as e:
            return e

    def add_cookie(self) -> dict[str, str]:
        """Function ini bertujuan agar otomatis masuk ke website GREE
        tanpa Authorization login
        """
        for cookie in GREE_COOKIE_TEMP:
            try:
                new_cookie: dict[str, Any] = {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie["domain"],
                    "path": cookie["path"],
                }

                if "expirationDate" in cookie and cookie["expirationDate"] is not None:
                    new_cookie["expiry"] = int(cookie["expirationDate"])

                self.driver.add_cookie(new_cookie)
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        return {"status": "success"}

    def upload_serial_number_image(self, file_path: GreeTicket, tipe):
        buttons = self.wait_for(
            description="All footer buttons",
            condition=EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".modal-footer button")
            ),
        )
        for btn in buttons:
            classes = btn.get_attribute("class")
            text = btn.text.strip()
            if "Button_blue__" in classes and text == "Upload":
                file_input = self.wait_for(
                    description=f"File input di {tipe}",
                    condition=EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[type='file'][accept='image/*']")
                    ),
                )
                self.driver.execute_script(
                    """
                   arguments[0].style.display = 'block';
                   arguments[0].style.visibility = 'visible';
               """,
                    file_input,
                )
                file_input.send_keys(
                    os.path.abspath(f"{PUBLIC_DIR}/{file_path.serial_number}")
                )
                btn.click()
                self.log("Berhasil klik tombol Upload")

               
                self.wait_for(
                    description="Menunggu modal tertutup",
                    condition=EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, ".modal-footer")
                    )
                )
                time.sleep(1) 
                return

    def click_serial_number(self, tipe: str = "Indoor"):
        
        time.sleep(1)  

        containers = self.wait_for(
            description="Mencari containers input-style-1",
            condition=EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".input-style-1.col-xl-4")
            ),
        )
        for container in containers:
            try:
                label = container.find_element(By.TAG_NAME, "label")
                if f"Nomor Seri ({tipe})" in label.text:
                    svg_button = container.find_element(By.CSS_SELECTOR, ".card-style")
                    self.log(f"Element dari ({tipe}) ditemukan")
                    svg_button.click()
                    self.upload_serial_number_image(self.ticket, tipe)
                    break
            except Exception as e:
                self.log(f"Element tidak ditemukan: {e}")

    def click_modification_button(self, max_attempts=5, delay=1):
        """
        Klik tombol modifikasi dengan mekanisme retry
        - max_attempts: Jumlah maksimal percobaan
        - delay: Jeda antar percobaan (detik)
        """

        for attempt in range(1, max_attempts + 1):
            try:
                modification_button = self.wait_for(
                    description=f"Mencoba klik button modifikasi (percobaan {attempt}/{max_attempts})",
                    condition=EC.element_to_be_clickable(
                        (By.XPATH, LOCATORS["button_modifikasi"])
                    ),
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    modification_button,
                )
                time.sleep(0.5)

                try:
                    modification_button.click()
                except (
                    StaleElementReferenceException,
                    ElementClickInterceptedException,
                ):
                    self.driver.execute_script(
                        "arguments[0].click();", modification_button
                    )

                return True

            except (TimeoutException, StaleElementReferenceException) as e:
                if attempt == max_attempts:
                    raise Exception(
                        f"Gagal klik tombol setelah {max_attempts} percobaan"
                    ) from e
                time.sleep(delay)

        return False

    def display_step_visit(self, max_attempts=5, delay=1):
        """
        Klik tombol Step Visit

        Digunakan setelah schedule
        """

        for attempt in range(1, max_attempts + 1):
            try:
                modification_button = self.wait_for(
                    description=f"Mencoba klik button visit (percobaan {attempt}/{max_attempts})",
                    condition=EC.element_to_be_clickable(
                        (By.XPATH, LOCATORS["button_visit"])
                    ),
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    modification_button,
                )
                time.sleep(0.5)

                try:
                    modification_button.click()
                    time.sleep(1.5)
                except (
                    StaleElementReferenceException,
                    ElementClickInterceptedException,
                ):
                    self.driver.execute_script(
                        "arguments[0].click();", modification_button
                    )

                return True

            except (TimeoutException, StaleElementReferenceException) as e:
                if attempt == max_attempts:
                    raise Exception(
                        f"Gagal klik tombol setelah {max_attempts} percobaan"
                    ) from e
                time.sleep(delay)

    def upload_in_step_visit(self, max_attempts=5, delay=1):
        try:
            uploaded_labels = set()

            for attempt in range(1, max_attempts + 1):
                boxes = self.wait_for(
                    description=f"Mencoba mendapatkan components_box (percobaan {attempt}/{max_attempts})",
                    condition=EC.presence_of_all_elements_located(
                        (By.XPATH, LOCATORS["display_next_step"])
                    ),
                )

                if not boxes:
                    raise Exception("Tidak ditemukan components_box")

                upload_found = False

                for box in boxes:
                    try:
                        label_text = box.find_element(By.XPATH, ".//span").text.strip()

                        if label_text in uploaded_labels:
                            continue

                        self.log(f"Label ditemukan: {label_text}")

                        unggah_btns = box.find_elements(
                            By.XPATH, ".//button[contains(normalize-space(), 'Unggah')]"
                        )

                        if not unggah_btns:
                            self.log(f"Tidak ada tombol Unggah untuk: {label_text}")
                            uploaded_labels.add(label_text)
                            continue

                        unggah_btn = unggah_btns[0]
                        self.driver.execute_script("arguments[0].click();", unggah_btn)
                        self.log(f"Klik tombol Unggah untuk: {label_text}")

                        self._upload_lokasi_and_navigation_route_in_next_step(
                            self.ticket
                        )

                        uploaded_labels.add(label_text)
                        upload_found = True

                        time.sleep(1)

                        break

                    except StaleElementReferenceException:
                        self.log("Stale element, akan re-fetch boxes...")
                        break
                    except Exception as e:
                        self.log(f"Error processing box: {e}")
                        continue

                if not upload_found:
                    button_save = self.wait_for(
                        description="Mencoba mendapatkan komponen simpan)",
                        condition=EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                LOCATORS["button_save_in_next_step"],
                            )
                        ),
                    )

                    button_save.click()
                    self.log("Semua upload selesai")
                    return

        except Exception as e:
            print("Error di upload_in_step_visit:", e)
            raise

    def _upload_lokasi_and_navigation_route_in_next_step(self, file_path: GreeTicket):
        buttons = self.wait_for(
            description="All footer buttons",
            condition=EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".modal-footer button")
            ),
        )

        for btn in buttons:
            classes = btn.get_attribute("class")
            text = btn.text.strip()

            if "Button_blue__" in classes and text == "Unggah":
                file_input = self.wait_for(
                    description="File input",
                    condition=EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "input[type='file'][accept='image/jpeg,image/png']",
                        )
                    ),
                )

                self.driver.execute_script(
                    """
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                """,
                    file_input,
                )

                file_input.send_keys(
                    os.path.abspath(f"{PUBLIC_DIR}/{file_path.serial_number}")
                )

                btn.click()
                self.log("Berhasil klik tombol Upload")

                return

    # def run(self):
    #     self.get_login_url()
    #     self.add_cookie()
    #     self.get_home_url()
    #     self.fill_no_work_order(self.ticket)
    #     self.click_edit_icon()
    #     # self.input_serial_number(tipe="Indoor")
    #     self.input_serial_number(tipe="Outdoor")
    #     # self.click_modification_button()

    def run(self):
        self._update_status("Login ke GREE", 20)
        self.get_login_url()
        self.add_cookie()

        self._update_status("Navigasi ke halaman utama", 40)
        self.get_home_url()

        self._update_status("Mengisi nomor work order", 60)
        self.fill_no_work_order(self.ticket)

        self._update_status("Membuka form edit", 70)
        self.click_edit_icon()

        self._update_status("Upload serial number", 85)
        self.click_serial_number(tipe="Outdoor")
        self.click_serial_number(tipe="Indoor")
        self._update_status("Finalisasi", 95)

        self.click_modification_button()
        self.display_step_visit()
        self.upload_in_step_visit()
