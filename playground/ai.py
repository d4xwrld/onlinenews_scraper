import requests

headers = {"Accept": "application/json"}

payload = {
    "messages": [
        {"role": "system", "content": "Nama Anda adalah Amba AI"},
        {"role": "user", "content": "Halo nama kamu siapa?"},
    ]
}

response = requests.post(
    "https://api.zpi.my.id/v1/ai/claude-3-sonnet", headers=headers, json=payload
)

data = response.json()
print(data)
