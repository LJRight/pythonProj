import datetime
import requests
import json

prefix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


url = "https://api.creatomate.com/v1/renders"
headers = {
    "Authorization": "Bearer 929260bbc9c24512bde07fe182f08f00243dc3f68c92fc8ec5789fa2a8a1122f636b0c04df95136ce9b29f137602f8f2",
    "Content-Type": "application/json",
}

data = {
    "template_id": "4b041952-d2c3-480f-a53c-90ef224379b1",
    "modifications": {
        "7f7e1331-941a-4b6f-89b7-cdc5372406cf": "가천대학교 정시모집",
        "48734f5c-8c90-41ac-a059-e949e733936b": "https://2f99-210-102-178-78.ngrok-free.app/static/sample_1.png",
        "0737f3b9-2968-4f40-a7ed-8297a340fa76": "https://2f99-210-102-178-78.ngrok-free.app/static/sample_2.png",
        "93efcf94-8c0f-4e50-8f6b-80c83beb4358": "https://2f99-210-102-178-78.ngrok-free.app/static/sample_3.png",
        "8ec7961e-6868-4ff7-879b-b2f6a939c9fe": "https://2f99-210-102-178-78.ngrok-free.app/static/sample_4.png",
        "2ae4b1f1-e254-4c08-8dbb-6b774855fd53": "https://2f99-210-102-178-78.ngrok-free.app/static/sample_5.png",
    },
}

response = requests.post(url, headers=headers, json=data)

with open(prefix + ".bin", "wb") as file:
    file.write(response.content)

print(response.content)

data = response.json()

for item in data:
    # 'url'과 'snapshot_url' 추출 (각 항목에 있는 경우)
    file_urls = [item.get("url"), item.get("snapshot_url")]

    for file_url in file_urls:
        if file_url:  # URL이 None이 아닌 경우에만 다운로드
            # 파일명 설정 (URL에서 파일명 추출)
            file_name = prefix + '_' + file_url.split('/')[-1]
            
            # URL에서 파일 다운로드
            print(f"Downloading {file_url}...")
            file_response = requests.get(file_url)
            
            # 다운로드한 파일을 저장
            with open(file_name, "wb") as file:
                file.write(file_response.content)
            print(f"File saved as {file_name}")

print(data)