import requests

url = "https://2f99-210-102-178-78.ngrok-free.app/static/sample_1.png"
response = requests.get(url)
with open("sample_1.png", "wb") as f:
    f.write(response.content)
