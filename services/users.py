from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.models import AppUser


def get_user(db: Session, clerk_user_id: str) -> AppUser | None:
    return db.get(AppUser, clerk_user_id)


def upsert_user(
    db: Session,
    clerk_user_id: str,
    *,
    admin_user_id: str | None = None,
    email: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    image_url: str | None = None,
) -> AppUser:
    user = get_user(db, clerk_user_id)
    if not user:
        user = AppUser(
            clerk_user_id=clerk_user_id,
            role="admin" if clerk_user_id == admin_user_id else "member",
        )
        db.add(user)

    for attribute, value in {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "image_url": image_url,
    }.items():
        if value is not None:
            setattr(user, attribute, value)

    if clerk_user_id == admin_user_id:
        user.role = "admin"

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, clerk_user_id: str) -> AppUser | None:
    user = get_user(db, clerk_user_id)
    if not user:
        return None

    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def set_user_active(db: Session, clerk_user_id: str, is_active: bool) -> AppUser | None:
    user = get_user(db, clerk_user_id)
    if not user:
        return None

    user.is_active = is_active
    user.deleted_at = None if is_active else datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user
