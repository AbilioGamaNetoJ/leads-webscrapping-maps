from types import SimpleNamespace

from openpyxl import load_workbook

from services.business_types import get_business_type
from services.xlsx_generator import generate_xlsx


def test_xlsx_headers_and_business_type_label():
    category = get_business_type("caca_vazamento")
    workbook = generate_xlsx(
        [
            SimpleNamespace(
                name="Exemplo",
                business_type="caca_vazamento",
                address="Rua A",
                phone="123",
                has_website=False,
                maps_url="",
            )
        ]
    )
    worksheet = load_workbook(workbook).active
    assert worksheet["A1"].value == "Nome do Negócio"
    assert worksheet["B1"].value == "Tipo de Negócio"
    assert worksheet["B2"].value == category.label
