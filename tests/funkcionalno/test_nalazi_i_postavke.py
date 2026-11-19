import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno


def test_moji_nalazi_sadrze_samo_vlastite_nalaze(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/nalazi/moji", headers=prijava("ana"))
    assert odgovor.status_code == 200
    nalazi = odgovor.json()
    assert len(nalazi) == 1
    assert nalazi[0]["id"] == 1
    assert nalazi[0]["naziv"] == "Krvna slika"
    assert nalazi[0]["datoteka"] == "nalaz-ana-krvna-slika.txt"


def test_preuzimanje_vlastite_datoteke_nalaza(client: TestClient, prijava) -> None:
    odgovor = client.get(
        "/api/nalazi/preuzmi", params={"datoteka": "nalaz-ana-krvna-slika.txt"}, headers=prijava("ana")
    )
    assert odgovor.status_code == 200
    assert "Pacijent: Ana Anić" in odgovor.text
    assert "Hemoglobin" in odgovor.text


def test_nalaz_u_json_formatu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/nalazi/2", params={"format": "json"}, headers=prijava("marko"))
    assert odgovor.status_code == 200
    assert odgovor.json()["naziv"] == "RTG kralježnice"
    assert "Pacijent: Marko Marić" in odgovor.json()["sadrzaj"]


def test_nalaz_u_pdf_formatu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/nalazi/1", params={"format": "pdf"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert odgovor.headers["content-type"].startswith("application/pdf")
    assert odgovor.content.startswith(b"%PDF")


def test_bez_parametra_format_nalaz_je_json(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/nalazi/1", headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert "Hemoglobin" in odgovor.json()["sadrzaj"]


def test_spremanje_postavki_u_yaml_formatu(client: TestClient, prijava) -> None:
    yaml = "podsjetnik: true\nsatiPrije: 24\nkanal: email\n"
    zaglavlja = {**prijava("marko"), "Content-Type": "application/yaml"}
    odgovor = client.post("/api/postavke", content=yaml, headers=zaglavlja)
    assert odgovor.status_code == 200
    assert odgovor.json()["postavke"] == {"podsjetnik": True, "satiPrije": 24, "kanal": "email"}


def test_spremljene_postavke_mogu_se_dohvatiti(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    spremanje = client.post(
        "/api/postavke",
        content="podsjetnik: false\nsatiPrije: 48\nkanal: sms\n",
        headers={**zaglavlja, "Content-Type": "text/plain"},
    )
    dohvat = client.get("/api/postavke", headers=zaglavlja)
    assert spremanje.status_code == 200
    assert dohvat.json()["postavke"] == {"podsjetnik": False, "satiPrije": 48, "kanal": "sms"}


def test_nepoznat_kanal_obavijesti_vraca_400(client: TestClient, prijava) -> None:
    odgovor = client.post(
        "/api/postavke",
        content="kanal: golub\n",
        headers={**prijava("ana"), "Content-Type": "application/yaml"},
    )
    assert odgovor.status_code == 400
