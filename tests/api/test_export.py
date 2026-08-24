from io import BytesIO

from openpyxl import load_workbook


def test_export_returns_xlsx(client, seeded_businesses):
    response = client.get("/export")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    worksheet = load_workbook(BytesIO(response.content)).active
    names = {worksheet[f"A{row}"].value for row in range(2, worksheet.max_row + 1)}
    assert names == {"Loja Com Site", "Padaria Sem Site"}


def test_export_only_without_website(client, seeded_businesses):
    response = client.get("/export", params={"only_without_website": True})
    assert response.status_code == 200
    worksheet = load_workbook(BytesIO(response.content)).active
    names = {worksheet[f"A{row}"].value for row in range(2, worksheet.max_row + 1)}
    assert names == {"Padaria Sem Site"}


def test_export_fills_every_column_with_the_business_own_data(client, seeded_businesses):
    with_site, without_site = seeded_businesses
    response = client.get("/export")
    assert response.status_code == 200

    worksheet = load_workbook(BytesIO(response.content)).active
    rows_by_name = {
        row[0].value: [cell.value for cell in row]
        for row in worksheet.iter_rows(min_row=2)
    }

    assert rows_by_name[with_site.name] == [
        with_site.name,
        "Loja de Roupas",
        with_site.address,
        with_site.phone,
        None,
        None,
        "Sim",
        with_site.maps_url,
    ]
    assert rows_by_name[without_site.name] == [
        without_site.name,
        "Padaria",
        without_site.address,
        without_site.phone,
        None,
        None,
        "Não",
        without_site.maps_url,
    ]
