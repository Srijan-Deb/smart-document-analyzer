import bcrypt
import sqlite3

# Get the first user's hash from the database
conn = sqlite3.connect('sql_app.db')
cursor = conn.execute('SELECT email, hashed_password FROM users WHERE email = "test@test.com"')
row = cursor.fetchone()
conn.close()

if row:
    email, stored_hash = row
    print(f"Email: {email}")
    print(f"Stored hash: {stored_hash}")
    print(f"Hash type: {type(stored_hash)}")
    print(f"Hash length: {len(stored_hash)}")
    
    # Test with common passwords
    for pwd in ['test123', 'password', 'test', '123456', 'testuser', 'test@test.com']:
        try:
            result = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"Password '{pwd}': {result}")
            if result:
                break
        except Exception as e:
            print(f"Password '{pwd}': ERROR - {e}")
else:
    print("No user found")

# Also check Srijan's user
conn = sqlite3.connect('sql_app.db')
cursor = conn.execute('SELECT email, hashed_password FROM users WHERE email = "srijan159753@gmail.com"')
row = cursor.fetchone()
conn.close()

if row:
    email, stored_hash = row
    print(f"\nEmail: {email}")
    print(f"Stored hash: {stored_hash}")
    print(f"Hash looks valid: {stored_hash.startswith('$2b$')}")

# Check user with 'pwd' as hash (row 9)
conn = sqlite3.connect('sql_app.db')
cursor = conn.execute('SELECT email, hashed_password FROM users WHERE hashed_password = "pwd"')
row = cursor.fetchone()
conn.close()

if row:
    email, stored_hash = row
    print(f"\n*** PROBLEM: User '{email}' has plain text password: '{stored_hash}' ***")
    print("This will crash bcrypt.checkpw()")
