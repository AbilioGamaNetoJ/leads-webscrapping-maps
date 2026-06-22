import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal
from database.models import Business

manual_mapping = {
    "Mamyn Banho e Tosa": "pet_store",
    "Billy & Toffy": "pet_store",
    "Paws and Roots": "pet_store",
    "Uai Di Minas": "restaurant",
    "Los Troncos Parrilla Uruguaya & Getúlio – Bar Secreto": "restaurant",
    "El Señor Asador de Brasa": "restaurant",
    "Marquês da Lagoa": "restaurant",
    "Jardín Del Mar": "restaurant",
    "Farma & Farma Campeche": "pharmacy",
    "Recanto da Mata": "restaurant" # Supposing it's a restaurant, or leave it. We'll set to restaurant for now.
}

def fix_remaining():
    with SessionLocal() as db:
        for name, b_type in manual_mapping.items():
            db.query(Business).filter(Business.name == name).update({"business_type": b_type})
        db.commit()
        print("Final missing items updated.")

if __name__ == "__main__":
    fix_remaining()
