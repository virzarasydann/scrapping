import requests
from bs4 import BeautifulSoup

BASE_URL = "https://fs.616263.my.id"
session = requests.Session()

# --- Step 1: Ambil token login ---
login_page = session.get(f"{BASE_URL}/login")
soup = BeautifulSoup(login_page.text, "html.parser")
csrf_login = soup.find("meta", {"name": "csrf_test_name"})["content"]

# --- Step 2: Login ---
login_payload = {
    "login": "ADMIN1",
    "password": "ADMINAC",
    "csrf_test_name": csrf_login
}
session.post(f"{BASE_URL}/login", data=login_payload)

# --- Step 3: Ambil token add job ---
add_page = session.get(f"{BASE_URL}/admin/jobs/add")

print(f"\n[GET ADD PAGE]")
print(f"Status: {add_page.status_code}")
print(f"URL: {add_page.url}")
print(f"Content length: {len(add_page.text)}")


soup_add = BeautifulSoup(add_page.text, "html.parser")
for inp in soup_add.find_all(["input", "textarea", "select"]):
    name = inp.get("name")
    if name:
        print("Field:", name)
csrf_add = soup_add.find("meta", {"name": "csrf_test_name"})["content"]

# --- Step 4: POST data ke form ---
payload = {
    "csrf_test_name": csrf_add,
    
    "id_customer": "1",                              # ← TAMBAHKAN
    "customer_address": "Jl. Test Integration No.1",
    "customer_phone_number": "081234567890",
    
    "id_ac_unit": "156",                               # ← TAMBAHKAN
    "id_service_type": "24",
    "description": "testing",
    "team": "AhliAC",
    "accessor": "Wahyu Nugraha",
    "start_date": "2025-11-07",
    "end_date": "2025-11-07",
    "save": "1"                                     # ← TAMBAHKAN (atau "")
}

response = session.post(f"{BASE_URL}/admin/jobs/add", data=payload)
print("\n" + "="*50)
print("[RESPONSE HEADERS]")
print("="*50)
for key, value in response.headers.items():
    print(f"{key}: {value}")

# print("\n" + "="*50)
# print("[RESPONSE DETAILS]")
# print("="*50)
# print(f"Status: {response.status_code}")
# print(f"Reason: {response.reason}")
# print(f"URL: {response.url}")
# print(f"Encoding: {response.encoding}")
# print(f"Content-Length: {len(response.content)}")
# print(f"Text Length: {len(response.text)}")
# print(f"Raw Content: {response.content}")
