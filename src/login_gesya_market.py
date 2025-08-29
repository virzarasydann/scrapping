import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:8000/admin/login")

title = driver.title
print(title)
driver.implicitly_wait(2)

username = driver.find_element(by=By.NAME, value="username")
password = driver.find_element(by=By.NAME, value="password")
loginButton = driver.find_element(by=By.CSS_SELECTOR, value=".btn-login")

username.send_keys("master")
password.send_keys("admin")
loginButton.click()


sidebar = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.nav-sidebar"))
)

driver.get("http://127.0.0.1:8000/admin/master/lokasi-kavling")
testModalClick = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-info"))
)

modal = driver.find_element(By.CSS_SELECTOR, ".btn-info")
modal.click()

driver.find_element(By.ID, "nama_kavling").send_keys("Kavling A-12")
driver.find_element(By.ID, "nama_singkat").send_keys("A12")
driver.find_element(By.ID, "header").send_keys("Perumahan Hijau")
driver.find_element(By.ID, "alamat").send_keys("Jl. Mawar No. 45")
driver.find_element(By.ID, "nama_perusahaan").send_keys("PT Hijau Indah")
driver.find_element(By.ID, "nama_mengetahui").send_keys("Bapak Budi")
driver.find_element(By.ID, "alamat_perusahaan").send_keys("Jl. Melati No. 20")
driver.find_element(By.ID, "informasi_rek").send_keys("123456789")
driver.find_element(By.ID, "telp_perusahaan").send_keys("021987654")
driver.find_element(By.ID, "kota_penandatangan").send_keys("Jakarta")
driver.find_element(By.ID, "nama_penandatangan").send_keys("Ibu Sari")
driver.find_element(By.ID, "jabatan_penandatangan").send_keys("Direktur")
driver.find_element(By.ID, "urutan").send_keys("1")
driver.find_element(By.ID, "kop_surat").send_keys(r"D:\test-scrapping\env\cover.jpg")
driver.find_element(By.ID, "bg_kwitansi").send_keys(r"D:\test-scrapping\env\cover.jpg")
driver.find_element(By.ID, "submitBtn").click()

# namaJalan = driver.find_element(by=By.ID, value="nama").send_keys("Testing Automation123")
# select_element = driver.find_element(By.ID, 'id_lokasi')
# select = Select(select_element)
# select.select_by_index(3)

# panjang = driver.find_element(by=By.ID, value="panjang").send_keys("100")
# lebar = driver.find_element(by=By.ID, value="lebar").send_keys("200")
# submit = driver.find_element(by=By.ID, value="submitBtn").click()
# options = select.options
# for opt in options:
#     print(opt.text, opt.get_attribute("value"))

input("Click enter untuk keluar")

driver.quit()
