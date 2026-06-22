import sys
from pathlib import Path

# Add project root to path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal
from database.models import Business

def check_null_types():
    with SessionLocal() as db:
        businesses = db.query(Business).filter(Business.business_type == None).all()
        print(f"Found {len(businesses)} businesses without type.")
        for b in businesses[:20]:
            print(f"ID: {b.id} | Name: {b.name}")
        if len(businesses) > 20:
            print("...")

if __name__ == "__main__":
    check_null_types()
