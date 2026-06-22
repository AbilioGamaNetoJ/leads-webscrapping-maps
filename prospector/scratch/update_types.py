import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal
from database.models import Business

def classify_name(name: str) -> str | None:
    n = name.lower()
    if any(k in n for k in ["barbearia", "barber"]):
        return "barber_shop"
    if any(k in n for k in ["pet", "agro", "veterin", "animal", "patinha", "cachorro", "gato", "bicho"]):
        return "pet_store"
    if any(k in n for k in ["farmácia", "farmacia", "drogaria"]):
        return "pharmacy"
    if any(k in n for k in ["padaria", "panificadora", "confeitaria", "cafe", "café"]):
        return "bakery"
    if any(k in n for k in ["restaurante", "lanchonete", "pizza", "hamburg", "lanches", "sushi", "bistrô"]):
        return "restaurant"
    if any(k in n for k in ["academia", "gym", "crossfit", "fitness"]):
        return "gym"
    if any(k in n for k in ["loja", "roupa", "modas", "boutique", "vestuário"]):
        return "clothing_store"
    if any(k in n for k in ["salão", "salao", "beleza", "cabeleireiro", "esmalteria", "make", "estetica", "estética", "hair"]):
        return "beauty_salon"
    if any(k in n for k in ["supermercado", "mercado", "mercearia", "atacadão", "atacadao"]):
        return "supermarket"
    if any(k in n for k in ["clinica", "clínica", "médic", "medic", "odonto", "dentist", "consultório", "consultorio"]):
        return "doctor"
    return None

def update_types():
    with SessionLocal() as db:
        businesses = db.query(Business).filter(getattr(Business, "business_type") == None).all()
        updated_count = 0
        unclassified = []
        for b in businesses:
            guessed_type = classify_name(str(b.name))
            if guessed_type:
                b.business_type = guessed_type  # type: ignore
                updated_count += 1
            else:
                unclassified.append(b.name)
        
        db.commit()
        print(f"Successfully updated {updated_count} businesses.")
        print(f"Could not classify {len(unclassified)} businesses.")
        if unclassified:
            print("Examples of unclassified:")
            for n in unclassified[:10]:
                print(f" - {n}")

if __name__ == "__main__":
    update_types()
