import pytest

from services.whatsapp import to_whatsapp_url


@pytest.mark.parametrize(
    ("phone", "expected"),
    [
        ("+55 48 98471-4240", "https://wa.me/5548984714240"),
        ("+55 48 3025-6255", "https://wa.me/5548930256255"),
        ("(48) 3025-6255", "https://wa.me/5548930256255"),
        ("48984714240", "https://wa.me/5548984714240"),
        ("Não informado", None),
        (None, None),
        ("123", None),
        ("", None),
    ],
)
def test_to_whatsapp_url(phone, expected):
    assert to_whatsapp_url(phone) == expected
