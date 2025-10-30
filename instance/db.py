# Update this part in your create_users.py file
import os

# Ensure the instance directory exists
os.makedirs('instance', exist_ok=True)

# Update the database URL to use an absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_path = os.path.join(project_root, 'instance', 'markmate.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)