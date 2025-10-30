"""
Register users on the deployed Render backend
"""
import requests
from urllib.parse import urlencode

API_BASE = "https://markmate-api-vbm1.onrender.com/api"

# Admin user (will be registered first and become admin automatically)
admin = {"username": "K.Nagaraju", "password": "IIITDMK"}

# Student users
students = [
    {"username": "Praneetha", "password": "123CS0053"},
    {"username": "Manasa", "password": "123CS0021"},
    {"username": "Sujith", "password": "123CS0025"},
    {"username": "Aarav Das", "password": "123CS0001"},
    {"username": "Aarav Gupta", "password": "123CS0002"},
    {"username": "Aarav Reddy", "password": "123CS0003"},
    {"username": "Aarav Saxena", "password": "123CS0004"},
    {"username": "Aditi Menon", "password": "123CS0005"},
    {"username": "Aditya Jain", "password": "123CS0006"},
    {"username": "Aditya Kulkarni", "password": "123CS0007"},
    {"username": "Aditya Shetty", "password": "123CS0008"},
    {"username": "Advait Bose", "password": "123CS0009"},
    {"username": "Advait Prasad", "password": "123CS0010"},
    {"username": "Akash Kulkarni", "password": "123CS0011"},
    {"username": "Akash Pathak", "password": "123CS0012"},
    {"username": "Aman Pillai", "password": "123CS0013"},
    {"username": "Aman Reddy", "password": "123CS0014"},
    {"username": "Amrita Bose", "password": "123CS0015"},
    {"username": "Amrita Mahajan", "password": "123CS0016"},
    {"username": "Anika Das", "password": "123CS0017"},
]

def register_user(username, password):
    """Register a single user"""
    url = f"{API_BASE}/auth/register?username={requests.utils.quote(username)}&password={requests.utils.quote(password)}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f"[OK] Registered: {username}")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"[SKIP] Already exists: {username}")
            return True
        else:
            print(f"[FAIL] Failed to register {username}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error registering {username}: {e}")
        return False

def main():
    print("=" * 60)
    print("Registering users on deployed backend")
    print(f"Backend: {API_BASE}")
    print("=" * 60)
    
    # Register admin first
    print("\n1. Registering Admin User...")
    register_user(admin["username"], admin["password"])
    
    # Register students
    print(f"\n2. Registering {len(students)} Student Users...")
    success_count = 0
    for student in students:
        if register_user(student["username"], student["password"]):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Registration Complete!")
    print(f"Successfully registered: {success_count + 1}/{len(students) + 1} users")
    print("=" * 60)
    print("\nYou can now log in at:")
    print("https://praneethaboya.github.io/MarkMate/login.html")
    print(f"\nAdmin credentials:")
    print(f"  Username: {admin['username']}")
    print(f"  Password: {admin['password']}")

if __name__ == "__main__":
    main()
