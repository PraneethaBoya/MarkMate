import json
import sys
import httpx

BASE = "http://127.0.0.1:8010/api"
USERNAME = "K.Nagaraju"
PASSWORD = "IIITDMK"

try:
    c = httpx.Client(timeout=300.0)
    # Login
    r = c.post(f"{BASE}/auth/login", data={"username": USERNAME, "password": PASSWORD})
    r.raise_for_status()
    token = r.json().get("access_token")
    assert token, "No token returned"
    headers = {"Authorization": f"Bearer {token}"}
    # Train
    r = c.post(f"{BASE}/train", headers=headers)
    r.raise_for_status()
    print("TRAIN RESPONSE:\n", json.dumps(r.json(), indent=2))
    # Metrics
    r = c.get(f"{BASE}/metrics")
    r.raise_for_status()
    print("\nMETRICS:\n", json.dumps(r.json(), indent=2))
except Exception as e:
    print("ERROR:", repr(e))
    sys.exit(1)
finally:
    try:
        c.close()
    except Exception:
        pass
