"""S03 – open redirect nakon prijave (CWE-601). Dopušten je samo lokalni put. ASVS v5.0.0-1.2.2 (L1)."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.sigurnost


@pytest.mark.parametrize("return_url", ["https://zlo.example/x", "//zlo.example", "/\\zlo.example"])
def test_vanjska_adresa_ne_preusmjerava_van(client: TestClient, return_url: str) -> None:
    odgovor = client.post(
        "/prijava", data={"username": "ana", "password": "Ana12345!", "returnUrl": return_url}
    )

    assert odgovor.status_code in (302, 303)
    assert "zlo.example" not in odgovor.headers["location"]
