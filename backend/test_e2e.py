import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_test():
    # 1. Register User
    print("--- 1. Registering User ---")
    test_email = f"test_{uuid.uuid4()}@example.com"
    test_username = f"user_{uuid.uuid4().hex[:8]}"
    test_password = "password123"
    
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": test_email,
        "username": test_username,
        "password": test_password
    })
    print("Register Status:", reg_res.status_code)
    print("Register Response:", reg_res.json())
    if reg_res.status_code != 200:
        print("Registration failed!")
        return

    # 2. Login User
    print("\n--- 2. Logging In ---")
    login_res = requests.post(f"{BASE_URL}/auth/login", data={
        "username": test_email,
        "password": test_password
    })
    print("Login Status:", login_res.status_code)
    if login_res.status_code != 200:
        print("Login failed!", login_res.text)
        return
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Obtained Token:", token[:20] + "...")

    # 3. Create dummy file and Upload
    print("\n--- 3. Uploading Document ---")
    with open("dummy.txt", "w") as f:
        f.write("The quick brown fox jumps over the lazy dog. The dog's name is Rex and the fox's name is Felix.")
    
    with open("dummy.txt", "rb") as f:
        files = {"file": ("dummy.txt", f, "text/plain")}
        upload_res = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files)
    
    print("Upload Status:", upload_res.status_code)
    print("Upload Response:", upload_res.json())
    if upload_res.status_code != 200:
        print("Upload failed!")
        return
        
    doc_id = upload_res.json().get("document_id")

    # 4. Fetch Documents list
    print("\n--- 4. Fetching Document List ---")
    list_res = requests.get(f"{BASE_URL}/documents/", headers=headers)
    print("List Status:", list_res.status_code)
    print("List Response:", list_res.json())

    # 5. Chat Query
    print("\n--- 5. Querying Chat API ---")
    chat_res = requests.post(f"{BASE_URL}/chat/", headers=headers, json={
        "query": "What is the name of the dog and the fox?",
        "document_ids": [doc_id]
    }, stream=True)
    print("Chat Status:", chat_res.status_code)
    if chat_res.status_code != 200:
        print("Chat Failed!", chat_res.text)
    else:
        print("Chat Answer: ", end="", flush=True)
        import json
        for line in chat_res.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: ") and line_str != "data: [DONE]":
                    data_str = line_str[6:]
                    try:
                        data = json.loads(data_str)
                        if "chunk" in data:
                            print(data["chunk"], end="", flush=True)
                    except Exception:
                        pass
        print()

if __name__ == "__main__":
    run_test()
