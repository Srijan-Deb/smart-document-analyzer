import requests
import json
import sys

# use the token from the running system if needed, or just create a user
def test_stream():
    # 1. Register/Login
    base_url = "http://127.0.0.1:8000/api/v1"
    res = requests.post(f"{base_url}/auth/login", data={"username": "test_ac0e73ad-97d4-4a5f-adda-c8ec59f429b3@example.com", "password": "password123"})
    if res.status_code != 200:
        # maybe user doesn't exist, let's create a fresh one
        res = requests.post(f"{base_url}/auth/register", json={"email": "test_stream@example.com", "username": "test_stream", "password": "password123"})
        res = requests.post(f"{base_url}/auth/login", data={"username": "test_stream@example.com", "password": "password123"})
        
    token = res.json()["access_token"]
    
    # 2. Upload doc
    with open("dummy.txt", "w") as f:
        f.write("The quick brown fox jumps over the lazy dog.")
    with open("dummy.txt", "rb") as f:
        res = requests.post(f"{base_url}/documents/upload", headers={"Authorization": f"Bearer {token}"}, files={"file": f})
    doc_id = res.json()["document_id"]
    
    # 3. Chat
    print("Sending chat request...")
    res = requests.post(f"{base_url}/chat/", headers={"Authorization": f"Bearer {token}"}, json={"query": "hello", "document_ids": [doc_id]}, stream=True)
    for line in res.iter_lines():
        if line:
            print("LINE:", line.decode('utf-8'))

if __name__ == "__main__":
    test_stream()
