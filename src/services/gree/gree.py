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
from src.schemas.gree.technician_work_orders_schema import MessageResponse as GreeTicket
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
        for char in workorder_code.work_orders_number:
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

    def _upload_serial_number_image_indoor(self, file_path: GreeTicket):
        rdelay(2, 2)

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
                print("3")
                file_input = self.wait_for(
                    description="File input di Indoor",
                    condition=EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[type='file'][accept='image/*']")
                    ),
                )

                rdelay(2, 2)

                self.driver.execute_script(
                    """
                   arguments[0].style.display = 'block';
                   arguments[0].style.visibility = 'visible';
               """,
                    file_input,
                )

                file_input.send_keys(
                    os.path.abspath(f"{PUBLIC_DIR}/{file_path.barcode_indoor}")
                )
                rdelay(2, 2)

                self.log("Berhasil  Upload")

                # self.wait_for(
                #     description="Menunggu modal tertutup",
                #     condition=EC.invisibility_of_element_located(
                #         (By.CSS_SELECTOR, ".modal-footer")
                #     ),
                # )
                time.sleep(1)
                return

    def _upload_serial_number_image_outdoor(self, file_path: GreeTicket):
        rdelay(2, 2)
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
                    description="File input di Outdoor",
                    condition=EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "input[type='file'][accept='image/*']",
                        )
                    ),
                )
                rdelay(2, 2)
                self.driver.execute_script(
                    """
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                """,
                    file_input,
                )
                file_input.send_keys(
                    os.path.abspath(f"{PUBLIC_DIR}/{file_path.barcode_outdoor}")
                )
                rdelay(2, 2)

                self.log("Berhasil  Upload")

                # self.wait_for(
                #     description="Menunggu modal tertutup",
                #     condition=EC.invisibility_of_element_located(
                #         (By.CSS_SELECTOR, ".modal-footer")
                #     ),
                # )
                time.sleep(1)
                return

    def click_serial_number_indoor(self):
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
                if "Nomor Seri (Indoor)" in label.text:
                    svg_button = container.find_element(By.CSS_SELECTOR, ".card-style")
                    self.log("Element dari (Indoor) ditemukan")
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                        svg_button,
                    )
                    time.sleep(2)

                    try:
                        svg_button.click()
                        self.log(" Berhasil klik (Indoor) dengan .click()")
                    except ElementClickInterceptedException:
                        self.log("Normal click gagal, menggunakan JavaScript click...")
                        self.driver.execute_script("arguments[0].click();", svg_button)
                        self.log(" Berhasil klik (Indoor) dengan JavaScript")

                    self._upload_serial_number_image_indoor(self.ticket)
                    break
            except Exception as e:
                self.log(f"Element tidak ditemukan: {e}")

    def click_serial_number_outdoor(self):
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
                if "Nomor Seri (Outdoor)" in label.text:
                    svg_button = container.find_element(By.CSS_SELECTOR, ".card-style")
                    self.log("Element dari (Outdoor) ditemukan")
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                        svg_button,
                    )
                    time.sleep(2)

                    try:
                        svg_button.click()
                        self.log(" Berhasil klik (Outdoor) dengan .click()")
                    except ElementClickInterceptedException:
                        self.log("Normal click gagal, menggunakan JavaScript click...")
                        self.driver.execute_script("arguments[0].click();", svg_button)
                        self.log(" Berhasil klik (Indoor) dengan JavaScript")

                    self._upload_serial_number_image_outdoor(self.ticket)
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
                time.sleep(2)

                try:
                    modification_button.click()
                    time.sleep(2)
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
        """
        Main orchestrator untuk upload Lokasi dan Navigation Route

        Flow:
        1. Upload Lokasi (index [1])
        2. Upload Navigation Route (index [2])
        3. Klik tombol Simpan
        """
        try:
            self.log("Memulai proses upload di Step Visit...")

            # Upload Lokasi
            self.upload_lokasi(max_attempts, delay)

            # Upload Navigation Route
            self.upload_navigation_route(max_attempts, delay)

            # Klik tombol Simpan
            # input("...")
            self.log("Semua upload selesai, klik tombol Simpan...")
            button_save = self.wait_for(
                description="Tombol Simpan di Next Step",
                condition=EC.element_to_be_clickable(
                    (By.XPATH, LOCATORS["button_save_in_next_step"])
                ),
            )
            button_save.click()
            self.log("Tombol Simpan berhasil diklik")

        except Exception as e:
            self.log(f"ERROR di upload_in_step_visit: {e}")
            raise

    def upload_lokasi(self, max_attempts=5, delay=1):
        """
        Upload file untuk field Lokasi (index [1])
        """
        xpath_lokasi = "(//div[@class='col-lg-6 col-md-6 col-sm-4 col-6'])[1]"

        for attempt in range(1, max_attempts + 1):
            try:
                self.log(f"[LOKASI] Percobaan {attempt}/{max_attempts}")

                # Tunggu dan dapatkan container Lokasi
                lokasi_container = self.wait_for(
                    description="Container Lokasi",
                    condition=EC.presence_of_element_located((By.XPATH, xpath_lokasi)),
                )

                # Cek label untuk konfirmasi
                label_element = lokasi_container.find_element(By.XPATH, ".//span")
                label_text = label_element.text.strip()
                self.log(f"[LOKASI] Label ditemukan: {label_text}")

                # Cari tombol Unggah
                unggah_btn = lokasi_container.find_element(
                    By.XPATH, ".//button[contains(normalize-space(), 'Unggah')]"
                )

                # Klik tombol Unggah
                self.driver.execute_script("arguments[0].click();", unggah_btn)
                self.log(f"[LOKASI]  Klik tombol Unggah untuk: {label_text}")

                # Upload file melalui modal
                self._upload_file_with_modal(self.ticket.foto_rumah_customer)
                self.log("[LOKASI]  Upload selesai")

                time.sleep(1)
                return True

            except StaleElementReferenceException:
                self.log(f"[LOKASI] Stale element, retry {attempt}/{max_attempts}...")
                time.sleep(delay)
                if attempt == max_attempts:
                    raise Exception(
                        "Gagal upload Lokasi setelah beberapa percobaan (stale element)"
                    )

            except Exception as e:
                self.log(f"[LOKASI] ERROR: {e}")
                if attempt == max_attempts:
                    raise Exception(f"Gagal upload Lokasi: {e}") from e
                time.sleep(delay)

    def upload_navigation_route(self, max_attempts=5, delay=1):
        """
        Upload file untuk field Navigation Route by Google Map (index [2])
        """
        xpath_navigation = "(//div[@class='col-lg-6 col-md-6 col-sm-4 col-6'])[2]"

        for attempt in range(1, max_attempts + 1):
            try:
                self.log(f"[NAVIGATION] Percobaan {attempt}/{max_attempts}")

                # Tunggu dan dapatkan container Navigation Route
                navigation_container = self.wait_for(
                    description="Container Navigation Route",
                    condition=EC.presence_of_element_located(
                        (By.XPATH, xpath_navigation)
                    ),
                )

                # Cek label untuk konfirmasi
                label_element = navigation_container.find_element(By.XPATH, ".//span")
                label_text = label_element.text.strip()
                self.log(f"[NAVIGATION] Label ditemukan: {label_text}")

                # Cari tombol Unggah
                unggah_btn = navigation_container.find_element(
                    By.XPATH, ".//button[contains(normalize-space(), 'Unggah')]"
                )

                # Klik tombol Unggah
                self.driver.execute_script("arguments[0].click();", unggah_btn)
                self.log(f"[NAVIGATION]  Klik tombol Unggah untuk: {label_text}")

                # Upload file melalui modal
                self._upload_file_with_modal(self.ticket.share_lokasi)
                self.log("[NAVIGATION]  Upload selesai")

                time.sleep(1)
                return True

            except StaleElementReferenceException:
                self.log(
                    f"[NAVIGATION] Stale element, retry {attempt}/{max_attempts}..."
                )
                time.sleep(delay)
                if attempt == max_attempts:
                    raise Exception(
                        "Gagal upload Navigation Route setelah beberapa percobaan (stale element)"
                    )

            except Exception as e:
                self.log(f"[NAVIGATION] ERROR: {e}")
                if attempt == max_attempts:
                    raise Exception(f"Gagal upload Navigation Route: {e}") from e
                time.sleep(delay)

    def _upload_file_with_modal(self, file_path: str):
        """
        Generic method untuk upload file melalui modal

        Args:
            file_path: GreeTicket object yang berisi serial_number

        Raises:
            Exception: Jika upload gagal
        """
        try:
            # Tunggu semua button di modal footer
            buttons = self.wait_for(
                description="Tombol di modal footer",
                condition=EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".modal-footer button")
                ),
            )

            # Cari tombol Unggah yang benar
            unggah_button_found = False
            for btn in buttons:
                classes = btn.get_attribute("class")
                text = btn.text.strip()

                if "Button_blue__" in classes and text == "Unggah":
                    unggah_button_found = True

                    # Tunggu file input
                    file_input = self.wait_for(
                        description="File input di modal",
                        condition=EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "input[type='file'][accept='image/jpeg,image/png']",
                            )
                        ),
                    )

                    # Make file input visible
                    self.driver.execute_script(
                        """
                            arguments[0].style.display = 'block';
                            arguments[0].style.visibility = 'visible';
                        """,
                        file_input,
                    )

                    # Upload file
                    print(f"Ini File Path {file_path}")
                    file_full_path = os.path.abspath(f"{PUBLIC_DIR}/{file_path}")
                    print(f"Ini File Full Path {PUBLIC_DIR}/{file_path}")
                    file_input.send_keys(file_full_path)

                    self.log(f"File berhasil di-upload: {file_path}")
                    time.sleep(1)  # Wait untuk processing

                    self.log("Tombol Unggah di modal berhasil diklik")
                    time.sleep(1)

                    break

            if not unggah_button_found:
                raise Exception("Tombol Unggah tidak ditemukan di modal footer")

        except Exception as e:
            self.log(f"ERROR di _upload_file_with_modal: {e}")
            raise

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
        self.click_serial_number_indoor()
        self.click_serial_number_outdoor()
        self._update_status("Finalisasi", 95)

        self.click_modification_button()
        self.display_step_visit()
        self.upload_in_step_visit()
