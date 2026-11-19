import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

FRONTEND = "http://localhost:5173"


def _polje(odgovor, naziv: str) -> list[str]:
    return [lijecnik[naziv] for lijecnik in odgovor.json()]


def test_lijecnici_po_prezimenu_uzlazno(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/lijecnici", params={"sort": "prezime", "smjer": "asc"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert _polje(odgovor, "prezime") == ["Babić", "Horvat", "Jurić", "Kovačević", "Novak", "Vuković"]


def test_lijecnici_po_prezimenu_silazno(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/lijecnici", params={"sort": "prezime", "smjer": "desc"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert _polje(odgovor, "prezime") == ["Vuković", "Novak", "Kovačević", "Jurić", "Horvat", "Babić"]


def test_lijecnici_po_imenu_i_specijalizaciji(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    po_imenu = client.get("/api/lijecnici", params={"sort": "ime", "smjer": "asc"}, headers=zaglavlja)
    po_specijalizaciji = client.get(
        "/api/lijecnici", params={"sort": "specijalizacija", "smjer": "asc"}, headers=zaglavlja
    )
    assert _polje(po_imenu, "ime") == ["Ema", "Ivan", "Luka", "Maja", "Petra", "Tomislav"]
    assert _polje(po_specijalizaciji, "specijalizacija")[0] == "Dermatologija"


def test_zadano_sortiranje_je_po_prezimenu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/lijecnici", headers=prijava("ana"))
    assert odgovor.status_code == 200
    prezimena = _polje(odgovor, "prezime")
    assert len(prezimena) == 6
    assert prezimena[0] == "Babić"


def test_popis_lijecnika_trazi_prijavu(client: TestClient) -> None:
    assert client.get("/api/lijecnici").status_code == 401


def test_cors_za_dopusteni_origin(client: TestClient) -> None:
    odgovor = client.get("/api/health", headers={"Origin": FRONTEND})
    assert odgovor.status_code == 200
    assert odgovor.headers.get("Access-Control-Allow-Origin") == FRONTEND
    assert odgovor.headers.get("Access-Control-Allow-Credentials") == "true"


def test_preflight_s_dopustenog_origina(client: TestClient) -> None:
    odgovor = client.options(
        "/api/ja",
        headers={
            "Origin": FRONTEND,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert 200 <= odgovor.status_code < 300
    assert odgovor.headers.get("Access-Control-Allow-Origin") == FRONTEND
