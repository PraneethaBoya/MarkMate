import json
import sys
import uuid
import httpx

BASE = "http://127.0.0.1:8010/api"
username = f"trainer_{uuid.uuid4().hex[:6]}"
password = "pass123"

with httpx.Client(timeout=180.0) as c:
    try:
        c.post(f"{BASE}/auth/register", params={"username": username, "password": password})
    except Exception as e:
        pass
    r = c.post(f"{BASE}/auth/login", data={"username": username, "password": password})
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        print("Login failed: no token", file=sys.stderr)
        sys.exit(1)
    r = c.post(f"{BASE}/train", headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))
