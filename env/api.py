from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
app = FastAPI()

@app.post("/run-automation")
def run_automation():
    start_time = time.time()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://proyek.gesyagroup.id/admin/login")

    # login
    driver.find_element(By.NAME, "username").send_keys("master")
    driver.find_element(By.NAME, "password").send_keys("admin")
    driver.find_element(By.CSS_SELECTOR, ".btn-login").click()

    title = driver.title
    driver.quit()

    response_time = round(time.time() - start_time, 2)

    return {"status": "success", "page_title": title, "response_time": f"{response_time} seconds"}

    start_time = time.time()
    driver.implicitly_wait(2)

    # contoh automation login
    username = driver.find_element(by=By.NAME, value="username")
    password = driver.find_element(by=By.NAME, value="password")
    loginButton = driver.find_element(by=By.CSS_SELECTOR, value=".btn-login")

    username.send_keys("master")
    password.send_keys("admin")
    loginButton.click()

    title = driver.title
    driver.quit()

    end_time = time.time()  # ⏱️ catat waktu selesai
    response_time = round(end_time - start_time, 2)  # detik (dibulatkan 2 angka desimal)

    return {
        "status": "success",
        "page_title": title,
        "response_time": f"{response_time} seconds"
    }
