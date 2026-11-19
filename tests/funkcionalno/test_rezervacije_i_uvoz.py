import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

# Termin 7 je rezerviran za posebne provjere i ne koristi se u ovim testovima.
IZUZETI_TERMIN = 7

XML = """<?xml version="1.0" encoding="UTF-8"?>
<termini>
  <termin>
    <lijecnikId>1</lijecnikId>
    <pocetak>2026-12-01T09:00</pocetak>
    <kapacitet>1</kapacitet>
    <napomena>Jutarnji termin</napomena>
  </termin>
</termini>
"""


def _uvoz(client: TestClient, zaglavlja: dict[str, str], xml: str):
    return client.post("/api/termini/uvoz", content=xml, headers={**zaglavlja, "Content-Type": "application/xml"})


def _novi_termin(client: TestClient, prijava, kapacitet: int) -> int:
    xml = (
        "<termini><termin><lijecnikId>1</lijecnikId><pocetak>2027-02-01T08:00</pocetak>"
        f"<kapacitet>{kapacitet}</kapacitet><napomena>Dodatni termin</napomena></termin></termini>"
    )
    odgovor = _uvoz(client, prijava("dr.horvat"), xml)
    assert odgovor.status_code == 200
    return odgovor.json()["termini"][0]["id"]


def _slobodan_termin(client: TestClient, zaglavlja: dict[str, str]) -> int:
    for termin in client.get("/api/termini", headers=zaglavlja).json():
        if termin["id"] != IZUZETI_TERMIN and termin["slobodno"] > 0:
            return termin["id"]
    raise AssertionError("nema slobodnog termina")


def _termin(client: TestClient, zaglavlja: dict[str, str], termin_id: int) -> dict:
    return next(t for t in client.get("/api/termini", headers=zaglavlja).json() if t["id"] == termin_id)


def _moje(client: TestClient, zaglavlja: dict[str, str]) -> list[int]:
    return [r["id"] for r in client.get("/api/rezervacije/moje", headers=zaglavlja).json()]


def _rezerviraj(client: TestClient, zaglavlja: dict[str, str], termin_id: int, napomena: str):
    return client.post(
        "/api/rezervacije",
        json={"terminId": termin_id, "napomena": napomena, "oib": "48291736504"},
        headers=zaglavlja,
    )


def test_termini_lijecnika_prikazuju_slobodna_mjesta(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/termini", params={"lijecnikId": 1}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    termini = odgovor.json()
    assert len(termini) >= 3
    for termin in termini:
        assert termin["lijecnikId"] == 1
        assert termin["slobodno"] == termin["kapacitet"] - termin["zauzeto"]


def test_nova_rezervacija_je_vidljiva_u_mojim_rezervacijama(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    odgovor = _rezerviraj(client, zaglavlja, _slobodan_termin(client, zaglavlja), "Prvi pregled")
    assert odgovor.status_code == 201
    assert odgovor.json()["napomena"] == "Prvi pregled"
    assert odgovor.json()["id"] in _moje(client, zaglavlja)


def test_rezervacija_popunjenog_termina_vraca_409(client: TestClient, prijava) -> None:
    termin_id = _novi_termin(client, prijava, 1)
    assert _rezerviraj(client, prijava("ana"), termin_id, "Kontrola").status_code == 201
    odgovor = _rezerviraj(client, prijava("marko"), termin_id, "Kontrola")
    assert odgovor.status_code == 409
    assert odgovor.json()["greska"] == "Nema slobodnih mjesta."


def test_neispravan_oib_vraca_400(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    odgovor = client.post(
        "/api/rezervacije",
        json={"terminId": _slobodan_termin(client, zaglavlja), "napomena": "Kontrola", "oib": "123"},
        headers=zaglavlja,
    )
    assert odgovor.status_code == 400


def test_vlasnik_moze_otkazati_vlastitu_rezervaciju(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    termin_id = _slobodan_termin(client, zaglavlja)
    rezervacija_id = _rezerviraj(client, zaglavlja, termin_id, "Otkazat ću").json()["id"]
    zauzeto_prije = _termin(client, zaglavlja, termin_id)["zauzeto"]

    odgovor = client.delete(f"/api/rezervacije/{rezervacija_id}", headers=zaglavlja)

    assert odgovor.status_code == 204
    assert rezervacija_id not in _moje(client, zaglavlja)
    assert _termin(client, zaglavlja, termin_id)["zauzeto"] == zauzeto_prije - 1


def test_potvrda_za_ispis_sadrzi_podatke_rezervacije(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    rezervacija_id = _rezerviraj(
        client, zaglavlja, _slobodan_termin(client, zaglavlja), "Molim jutarnji termin"
    ).json()["id"]
    odgovor = client.get(f"/ispis/rezervacije/{rezervacija_id}", headers=zaglavlja)
    assert odgovor.status_code == 200
    assert odgovor.headers["content-type"].startswith("text/html")
    assert "Potvrda rezervacije" in odgovor.text
    assert "Molim jutarnji termin" in odgovor.text


def test_lijecnik_uvozi_termine_iz_xml(client: TestClient, prijava) -> None:
    zaglavlja = prijava("dr.horvat")
    odgovor = _uvoz(client, zaglavlja, XML)
    assert odgovor.status_code == 200
    assert odgovor.json()["uvezeno"] == 1
    termin = odgovor.json()["termini"][0]
    assert termin["napomena"] == "Jutarnji termin"
    termini = client.get("/api/termini", params={"lijecnikId": 1}, headers=zaglavlja).json()
    assert termin["id"] in [t["id"] for t in termini]


def test_administrator_moze_uvoziti_termine(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("admin"), XML).status_code == 200


def test_korisnik_ne_moze_uvoziti_termine(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("ana"), XML).status_code == 403


def test_neispravan_xml_vraca_400(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("dr.horvat"), "<termini><termin>").status_code == 400
