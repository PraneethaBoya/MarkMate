"""
Train the ML model on the deployed backend
"""
import requests
import sys

BASE = "https://markmate-api-vbm1.onrender.com/api"
username = "K.Nagaraju"
password = "IIITDMK"

print("=" * 60)
print("Training ML Model on Deployed Backend")
print(f"Backend: {BASE}")
print("=" * 60)

try:
    # Login as admin
    print("\n1. Logging in as admin...")
    r = requests.post(f"{BASE}/auth/login", data={"username": username, "password": password})
    r.raise_for_status()
    token = r.json().get("access_token")
    
    if not token:
        print("[ERROR] Login failed: no token")
        sys.exit(1)
    
    print("[OK] Logged in successfully")
    
    # Train the model
    print("\n2. Training model (this may take a minute)...")
    r = requests.post(
        f"{BASE}/train", 
        headers={"Authorization": f"Bearer {token}"},
        timeout=180.0
    )
    r.raise_for_status()
    
    result = r.json()
    print("\n[OK] Training complete!")
    print(f"\nResults:")
    print(f"  Best Model: {result.get('best_model', 'N/A')}")
    print(f"  Accuracy: {result.get('accuracy', 'N/A')}")
    print(f"  Precision: {result.get('precision', 'N/A')}")
    print(f"  Recall: {result.get('recall', 'N/A')}")
    print(f"  F1 Score: {result.get('f1', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("Model training successful!")
    print("=" * 60)
    
except requests.exceptions.HTTPError as e:
    print(f"\n[ERROR] HTTP Error: {e}")
    print(f"Response: {e.response.text if e.response else 'N/A'}")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)
