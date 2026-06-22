import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal
from database.models import Business

def fix_dog_island():
    with SessionLocal() as db:
        # Find anything with 'dog' or 'canina' that was misclassified as beauty_salon
        businesses = db.query(Business).filter(getattr(Business, "business_type") == 'beauty_salon').all()
        updated_count = 0
        for b in businesses:
            n = b.name.lower()
            if 'dog' in n or 'canina' in n or 'pet' in n or 'cachorro' in n or 'cão' in n or 'cao ' in n:
                print(f"Fixing {b.name} from beauty_salon to pet_store")
                b.business_type = 'pet_store'  # type: ignore
                updated_count += 1
        
        db.commit()
        print(f"Fixed {updated_count} misclassified pet shops.")

if __name__ == "__main__":
    fix_dog_island()
