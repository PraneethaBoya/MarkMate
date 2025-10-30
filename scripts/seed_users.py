import os, sys
from pathlib import Path

# Ensure project root is on sys.path so 'backend' can be imported when running as a script
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.models import SessionLocal, User, init_db
from backend.auth import get_password_hash

def ensure_user(db, username: str, raw_password: str, role: str = "student", full_name: str | None = None):
    u = db.query(User).filter(User.username == username).first()
    if u:
        # ensure role is correct
        changed = False
        if u.role != role:
            u.role = role
            changed = True
        # ensure password matches requested one
        new_hash = get_password_hash(raw_password)
        if u.password_hash != new_hash:
            u.password_hash = new_hash
            changed = True
        # ensure full_name if provided
        if full_name is not None and u.full_name != full_name:
            u.full_name = full_name
            changed = True
        if changed:
            db.add(u)
            db.commit()
        return False
    u = User(username=username, password_hash=get_password_hash(raw_password), role=role, full_name=full_name)
    db.add(u)
    db.commit()
    return True

def main():
    init_db()
    db = SessionLocal()
    created = 0
    created += 1 if ensure_user(db, "K.Nagaraju", "IIITDMK", role="administrator") else 0
    created += 1 if ensure_user(db, "Praneetha", "123CS0053", role="student") else 0
    created += 1 if ensure_user(db, "Sujith", "123CS0025", role="student") else 0
    created += 1 if ensure_user(db, "Manasa", "123CS0021", role="student") else 0
    # Batch students 01..10
    batch = [
        ("123CS0001", "123CS0001", "Aditi Sharma"),
        ("123CS0002", "123CS0002", "Rahul Verma"),
        ("123CS0003", "123CS0003", "Meera Reddy"),
        ("123CS0004", "123CS0004", "Arjun Nair"),
        ("123CS0005", "123CS0005", "Priya Singh"),
        ("123CS0006", "123CS0006", "Karan Patel"),
        ("123CS0007", "123CS0007", "Simran Kaur"),
        ("123CS0008", "123CS0008", "Akash Mehta"),
        ("123CS0009", "123CS0009", "Sneha Joshi"),
        ("123CS0010", "123CS0010", "Vivek Sinha"),
    ]
    for roll_user, passw, full_name in batch:
        # Only keep name-as-username with password=roll
        created += 1 if ensure_user(db, full_name, passw, role="student", full_name=full_name) else 0
    db.close()
    print(f"Seed complete. New users created: {created}")

if __name__ == "__main__":
    main()
