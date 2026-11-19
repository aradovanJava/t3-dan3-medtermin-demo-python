"""S01 – IDOR kod brisanja (CWE-639). Alat ne zna čiji je zapis, pa ovo provjeravamo testom s dva korisnika.
WSTG-ATHZ-04 · ASVS v5.0.0-8.2.2 (L1)."""

import pytest
from fastapi.testclient import TestClient

from tests.sigurnost.conftest import rezerviraj

pytestmark = pytest.mark.sigurnost


def _moje(client: TestClient, zaglavlja: dict[str, str]) -> list[int]:
    return [r["id"] for r in client.get("/api/rezervacije/moje", headers=zaglavlja).json()]


def test_marko_ne_moze_obrisati_aninu_rezervaciju(client: TestClient, prijava, novi_termin) -> None:
    ana, marko = prijava("ana"), prijava("marko")
    nova = rezerviraj(client, ana, novi_termin(1), "Kontrolni pregled")
    assert nova.status_code == 201
    rezervacija_id = nova.json()["id"]

    brisanje = client.delete(f"/api/rezervacije/{rezervacija_id}", headers=marko)

    assert brisanje.status_code in (403, 404), "tuđi zapis: 403 ili 404, nikako 204"
    assert rezervacija_id in _moje(client, ana), "ana i dalje vidi svoju rezervaciju"


def test_vlasnik_moze_otkazati_svoju(client: TestClient, prijava, novi_termin) -> None:
    ana = prijava("ana")
    rezervacija_id = rezerviraj(client, ana, novi_termin(1), "Otkazujem").json()["id"]

    assert client.delete(f"/api/rezervacije/{rezervacija_id}", headers=ana).status_code == 204
    assert rezervacija_id not in _moje(client, ana)
