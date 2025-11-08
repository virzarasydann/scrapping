import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://fs.616263.my.id"
LOGIN_URL = f"{BASE_URL}/login"
JOBS_JSON_URL = f"{BASE_URL}/admin/jobs/json"

session = requests.Session()

# --- Step 1: Ambil token CSRF dari halaman login ---
login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, "html.parser")

csrf_tag = soup.find("meta", {"name": "csrf_test_name"})
if not csrf_tag:
    raise Exception("CSRF token tidak ditemukan di halaman login!")

csrf_token = csrf_tag["content"]
print(f"[CSRF Token] {csrf_token}")

# --- Step 2: Login ---
login_payload = {
    "login": "ADMIN1",
    "password": "ADMINAC",
    "csrf_test_name": csrf_token
}

login_response = session.post(LOGIN_URL, data=login_payload)
print(f"[LOGIN STATUS] {login_response.status_code}")

# --- Step 3: GET data JSON dari /admin/jobs/json ---
jobs_response = session.get(JOBS_JSON_URL)
print(f"[GET JOBS STATUS] {jobs_response.status_code}")

# --- Step 4: Cek dan tampilkan hasil JSON ---
try:
    data = jobs_response.json()
    if isinstance(data, dict):  
        # misal JSON-nya {"menu": [...]} atau {"data": [...]}
        key_with_list = next((k for k, v in data.items() if isinstance(v, list)), None)
        if key_with_list:
            items = data[key_with_list]
        else:
            items = []
    else:
        # kalau JSON langsung list
        items = data

    if items:
        last_item = items[-1]
        print("=== Data terakhir ===")
        for k, v in last_item.items():
            print(f"{k}: {v}")
    else:
        print("Tidak ada data ditemukan.")
except Exception as e:
    print("[ERROR] Bukan JSON, tampilan mentah di bawah ini:")
    print(jobs_response.text[:500])
