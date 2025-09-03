import requests

payload = {
    "url": "https://picsum.photos/id/0/5000/3333",
    "extension": "jpg",
    "message": "#LAPOR Kabel putus",
    "name": "Azam",
    "pengirim": "08123",
    "location": "Balikpapan"
}

res = requests.post("http://localhost:8000/webhook", json=payload)
print(res.json())
