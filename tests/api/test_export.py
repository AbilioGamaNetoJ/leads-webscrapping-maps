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
