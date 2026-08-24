from collections.abc import Sequence

from sqlalchemy.orm import Session
from database.models import Business

# SQLite aceita no máximo 999 parâmetros por statement.
_ID_CHUNK_SIZE = 500


def place_id_exists(db: Session, place_id: str) -> bool:
    return db.query(Business).filter(Business.place_id == place_id).first() is not None


def existing_place_ids(db: Session, place_ids: Sequence[str]) -> set[str]:
    """Quais destes place_ids já estão no banco, em um único round-trip por bloco."""
    unique_ids = list(dict.fromkeys(place_ids))
    found: set[str] = set()

    for start in range(0, len(unique_ids), _ID_CHUNK_SIZE):
        chunk = unique_ids[start : start + _ID_CHUNK_SIZE]
        rows = db.query(Business.place_id).filter(Business.place_id.in_(chunk)).all()
        found.update(row[0] for row in rows)

    return found
