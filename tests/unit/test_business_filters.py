from database.models import Business
from services.business_filters import apply_business_filters


def test_business_filters_combine_name_website_and_type(db_session):
    matching = Business(
        place_id="matching",
        name="Padaria Central",
        has_website=False,
        business_type="bakery",
    )
    db_session.add_all(
        [
            matching,
            Business(
                place_id="wrong-site",
                name="Padaria com Site",
                has_website=True,
                business_type="bakery",
            ),
            Business(
                place_id="wrong-type",
                name="Padaria de Roupas",
                has_website=False,
                business_type="clothing_store",
            ),
        ]
    )
    db_session.commit()

    businesses = apply_business_filters(
        db_session.query(Business),
        name="padaria",
        has_website="false",
        business_type="bakery",
    ).all()

    assert businesses == [matching]
