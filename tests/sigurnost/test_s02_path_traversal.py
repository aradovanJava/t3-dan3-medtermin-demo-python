"""S02 – path traversal kod preuzimanja datoteke (CWE-22). Kanarinac izvan mape s dokumentima ne smije se moći
pročitati, ni kad mu ime sadrži korisničko ime. WSTG-ATHZ-01 · ASVS v5.0.0-5.3.2 (L1)."""

import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.sigurnost


def test_kanarinac_izvan_mape_nije_dostupan(client: TestClient, prijava, mape) -> None:
    sadrzaj = f"KANARINAC-{uuid.uuid4()}"
    ime = f"tajna-ana-{uuid.uuid4()}.txt"
    (mape.dokumenti.parent / ime).write_text(sadrzaj, encoding="utf-8")

    odgovor = client.get("/api/nalazi/preuzmi", params={"datoteka": f"../{ime}"}, headers=prijava("ana"))

    assert odgovor.status_code != 200
    assert sadrzaj not in odgovor.text
