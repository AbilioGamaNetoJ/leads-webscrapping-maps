from sqlalchemy.orm import Query

from database.models import Business


def apply_business_filters(
    query: Query,
    *,
    name: str = "",
    has_website: str = "",
    business_type: str = "",
) -> Query:
    if name:
        query = query.filter(Business.name.ilike(f"%{name}%"))

    if has_website == "true":
        query = query.filter(Business.has_website.is_(True))
    elif has_website == "false":
        query = query.filter(Business.has_website.is_(False))

    if business_type:
        query = query.filter(Business.business_type == business_type)

    return query
