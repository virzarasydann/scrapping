import requests

payload = {
    "url": "https://picsum.photos/id/0/5000/3333",
    "extension": "jpg",
    "message": "Kabel putus",
    "name": "Azam",
    "pengirim": "081232167185",
    "location": "Balikpapan"
}

# payload = {
#     "url": "",
#     "extension": "",
#     "message": "#lapor",
#     "name": "",
#     "pengirim": "081232167185",
#     "location": ""
# }


# payload = {
#     "url": "",
#     "extension": "",
#     "message": "#selesai",
#     "name": "",
#     "pengirim": "081232167185",
#     "location": ""
# }

# payload = {
#     "url": "",
#     "extension": "",
#     "message": "halo",
#     "name": "",
#     "pengirim": "081232167185",
#     "location": ""
# }

res = requests.post("http://localhost:8000/api/v1/webhook", json=payload)
print(res.json())
