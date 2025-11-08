import requests
from bs4 import BeautifulSoup

BASE_URL = "https://fs.616263.my.id"
LOGIN_URL = f"{BASE_URL}/login"
EDIT_JOB_URL = f"{BASE_URL}/admin/job-details/edit/4813"

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

# --- Step 3: GET halaman edit job ---
edit_page = session.get(EDIT_JOB_URL)
print(f"[EDIT PAGE STATUS] {edit_page.status_code}")
print(f"URL: {edit_page.url}")

# --- Step 4: Cari form dengan ID jobDetailForm ---
soup_edit = BeautifulSoup(edit_page.text, "html.parser")

# Cari form berdasarkan ID
form = soup_edit.find("form", {"id": "jobDetailForm"})

if not form:
    print("\n[ERROR] Form dengan id='jobDetailForm' tidak ditemukan!")
    print("\n=== SEMUA FORM YANG ADA ===")
    for f in soup_edit.find_all("form"):
        print(f"Form ID: {f.get('id', 'N/A')}, Action: {f.get('action', 'N/A')}")
else:
    print(f"\n[FORM DITEMUKAN]")
    print(f"  ID: {form.get('id')}")
    print(f"  Method: {form.get('method')}")
    print(f"  Action: {form.get('action')}")
    print(f"  Enctype: {form.get('enctype')}")
    
    print("\n" + "="*80)
    print("=== SEMUA FIELD DI DALAM FORM jobDetailForm ===")
    print("="*80)
    
    field_count = 0
    
    # Ambil semua input, textarea, dan select HANYA dari dalam form ini
    for tag in form.find_all(["input", "textarea", "select"]):
        field_count += 1
        name = tag.get("name", "")
        field_type = tag.get("type", tag.name)  # Untuk input ambil type, untuk textarea/select ambil tag name
        value = tag.get("value", "")
        required = "✓" if tag.get("required") else ""
        disabled = "✓" if tag.get("disabled") else ""
        readonly = "✓" if tag.get("readonly") else ""
        
        print(f"\n[{field_count}] {tag.name.upper()}")
        print(f"  Name: {name}")
        print(f"  Type: {field_type}")
        print(f"  Value: {value}")
        
        # Untuk select, tampilkan options
        if tag.name == "select":
            options = tag.find_all("option")
            print(f"  Options ({len(options)}):")
            for opt in options[:10]:  # Maksimal 10 options untuk tidak terlalu panjang
                opt_value = opt.get("value", "")
                opt_text = opt.get_text(strip=True)
                selected = " [SELECTED]" if opt.get("selected") else ""
                print(f"    - value='{opt_value}' → {opt_text}{selected}")
            if len(options) > 10:
                print(f"    ... dan {len(options) - 10} options lainnya")
        
        # Untuk textarea, tampilkan isi
        if tag.name == "textarea":
            content = tag.get_text(strip=True)
            if content:
                print(f"  Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        
        # Atribut tambahan
        attrs = []
        if required:
            attrs.append("REQUIRED")
        if disabled:
            attrs.append("DISABLED")
        if readonly:
            attrs.append("READONLY")
        if tag.get("accept"):
            attrs.append(f"Accept: {tag.get('accept')}")
        if tag.get("multiple"):
            attrs.append("MULTIPLE")
        if tag.get("class"):
            attrs.append(f"Class: {' '.join(tag.get('class'))}")
        
        if attrs:
            print(f"  Attributes: {', '.join(attrs)}")
    
    print("\n" + "="*80)
    print(f"Total field ditemukan: {field_count}")
    print("="*80)
    
    # --- Step 5: Generate payload template ---
    print("\n\n=== PAYLOAD TEMPLATE (Python Dict) ===\n")
    print("payload = {")
    
    for tag in form.find_all(["input", "textarea", "select"]):
        name = tag.get("name", "")
        if name:
            field_type = tag.get("type", tag.name)
            value = tag.get("value", "")
            
            # Skip file inputs
            if field_type == "file":
                print(f'    "{name}": "",  # FILE INPUT - handle separately')
            else:
                print(f'    "{name}": "{value}",')
    
    print("}")
    
    # --- Step 6: Generate FormData template untuk file uploads ---
    print("\n\n=== FORMDATA TEMPLATE (Python aiohttp) ===\n")
    print("from aiohttp import FormData")
    print("\nform = FormData()")
    
    for tag in form.find_all(["input", "textarea", "select"]):
        name = tag.get("name", "")
        if name:
            field_type = tag.get("type", tag.name)
            value = tag.get("value", "")
            
            if field_type == "file":
                accept = tag.get("accept", "")
                print(f'# form.add_field("{name}", open("file.jpg", "rb"), filename="file.jpg", content_type="image/jpeg")  # {accept}')
            else:
                print(f'form.add_field("{name}", "{value}")')