import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://proyek.gesyagroup.id/admin/login")

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

driver.get("https://proyek.gesyagroup.id/admin/OP-jalan/jalan")
testModalClick = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@data-target='#modalForm']"))
)

modal = driver.find_element(By.XPATH, "//button[@data-target='#modalForm']")
modal.click()

namaJalan = driver.find_element(by=By.ID, value="nama").send_keys("Testing Automation123")
select_element = driver.find_element(By.ID, 'id_lokasi')
select = Select(select_element)
select.select_by_index(3)

panjang = driver.find_element(by=By.ID, value="panjang").send_keys("100")
lebar = driver.find_element(by=By.ID, value="lebar").send_keys("200")
submit = driver.find_element(by=By.ID, value="submitBtn").click()
# options = select.options
# for opt in options:
#     print(opt.text, opt.get_attribute("value"))

input("Click enter untuk keluar")

driver.quit()
