import requests

# Test 1: Try login with form data (OAuth2 style)
print("=== Test 1: Login with form data ===")
r = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    data={'username': 'srijan159753@gmail.com', 'password': 'test123'},
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
print()

# Test 2: Try register a new user
print("=== Test 2: Register new test user ===")
r = requests.post(
    'http://localhost:8000/api/v1/auth/register',
    json={'email': 'logintest@test.com', 'username': 'logintest', 'password': 'test123'}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
print()

# Test 3: Login with the newly registered user
print("=== Test 3: Login with new user ===")
r = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    data={'username': 'logintest@test.com', 'password': 'test123'},
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
print()

# Test 4: Check the health endpoint
print("=== Test 4: Health check ===")
r = requests.get('http://localhost:8000/health')
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
