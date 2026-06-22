import sys
from pathlib import Path

# Add project root to path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.connection import engine
from sqlalchemy import text

def migrate():
    with engine.begin() as conn:
        print("Checking if column 'business_type' exists...")
        # A simple way for postgres/neon:
        try:
            conn.execute(text("ALTER TABLE businesses ADD COLUMN business_type VARCHAR;"))
            print("Migration successful: column 'business_type' added.")
        except Exception as e:
            if 'already exists' in str(e):
                print("Column 'business_type' already exists.")
            else:
                print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
