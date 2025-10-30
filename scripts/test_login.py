"""
Test login functionality on the deployed backend
"""
import requests

API_BASE = "https://markmate-api-vbm1.onrender.com/api"

def test_login(username, password):
    """Test login with given credentials"""
    print(f"\nTesting login for: {username}")
    print("=" * 50)
    
    # Prepare form data (OAuth2PasswordRequestForm format)
    data = {
        'username': username,
        'password': password
    }
    
    try:
        # Make login request
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=data,  # Use data parameter for form-encoded
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ LOGIN SUCCESSFUL!")
            print(f"  Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"  Username: {result.get('username', 'N/A')}")
            print(f"  Role: {result.get('role', 'N/A')}")
            return True
        else:
            print(f"\n✗ LOGIN FAILED!")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def main():
    print("=" * 50)
    print("Testing MarkMate Login")
    print("=" * 50)
    
    # Test admin login
    print("\n1. Testing Admin Login...")
    test_login("K.Nagaraju", "IIITDMK")
    
    # Test student login
    print("\n2. Testing Student Login...")
    test_login("Praneetha", "123CS0053")
    
    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
