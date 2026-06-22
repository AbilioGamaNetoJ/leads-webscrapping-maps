from sqlalchemy.orm import Session
from database.models import Business


def place_id_exists(db: Session, place_id: str) -> bool:
    return db.query(Business).filter(Business.place_id == place_id).first() is not None
