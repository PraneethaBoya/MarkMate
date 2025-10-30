import sys
import os
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import your modules
from backend.models import User, Base
from backend.auth import get_password_hash

# Database connection - update this to match your database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./instance/markmate.db"  # Update this for your database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# User data
users = [
    # Admin user - will be registered first
    {"username": "K.Nagaraju", "password": "IIITDMK", "full_name": "K. Nagaraju", "role": "administrator"},
    
    # Student users
    {"username": "Praneetha", "password": "123CS0053", "full_name": "Praneetha", "role": "student"},
    {"username": "Manasa", "password": "123CS0021", "full_name": "Manasa", "role": "student"},
    {"username": "Sujith", "password": "123CS0025", "full_name": "Sujith", "role": "student"},
    {"username": "Sowmya", "password": "123CS0026", "full_name": "Sowmya", "role": "student"},
    {"username": "Aarav Das", "password": "123CS0001", "full_name": "Aarav Das", "role": "student"},
    {"username": "Aarav Gupta", "password": "123CS0002", "full_name": "Aarav Gupta", "role": "student"},
    {"username": "Aarav Reddy", "password": "123CS0003", "full_name": "Aarav Reddy", "role": "student"},
    {"username": "Aarav Saxena", "password": "123CS0004", "full_name": "Aarav Saxena", "role": "student"},
    {"username": "Aditi Menon", "password": "123CS0005", "full_name": "Aditi Menon", "role": "student"},
    {"username": "Aditya Jain", "password": "123CS0006", "full_name": "Aditya Jain", "role": "student"},
    {"username": "Aditya Kulkarni", "password": "123CS0007", "full_name": "Aditya Kulkarni", "role": "student"},
    {"username": "Aditya Shetty", "password": "123CS0008", "full_name": "Aditya Shetty", "role": "student"},
    {"username": "Advait Bose", "password": "123CS0009", "full_name": "Advait Bose", "role": "student"},
    {"username": "Advait Prasad", "password": "123CS0010", "full_name": "Advait Prasad", "role": "student"},
    {"username": "Akash Kulkarni", "password": "123CS0011", "full_name": "Akash Kulkarni", "role": "student"},
    {"username": "Akash Pathak", "password": "123CS0012", "full_name": "Akash Pathak", "role": "student"},
    {"username": "Aman Pillai", "password": "123CS0013", "full_name": "Aman Pillai", "role": "student"},
    {"username": "Aman Reddy", "password": "123CS0014", "full_name": "Aman Reddy", "role": "student"},
    {"username": "Amrita Bose", "password": "123CS0015", "full_name": "Amrita Bose", "role": "student"},
    {"username": "Amrita Mahajan", "password": "123CS0016", "full_name": "Amrita Mahajan", "role": "student"},
    {"username": "Anika Das", "password": "123CS0017", "full_name": "Anika Das", "role": "student"}
]

def create_user(db: Session, user_data: dict) -> bool:
    """Create a user if they don't already exist"""
    if db.query(User).filter(User.username == user_data["username"]).first():
        print(f"User {user_data['username']} already exists")
        return False
    
    user = User(
        username=user_data["username"],
        password_hash=get_password_hash(user_data["password"]),
        full_name=user_data["full_name"],
        role=user_data["role"]
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created {user_data['role']}: {user_data['username']}")
    return True

def main():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    created = 0
    
    try:
        # Create admin first
        if create_user(db, users[0]):
            created += 1
        
        # Then create students
        for user in users[1:]:
            if create_user(db, user):
                created += 1
        
        print(f"\nSuccessfully created {created} users")
        print(f"Admin login: K.Nagaraju / IIITDMK")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()