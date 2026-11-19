"""S09 – pohranjeni XSS na stranici za ispis (CWE-79). Pasivni ZAP ne sprema unos i ne otvara ispis.
WSTG-INPV-02 · ASVS v5.0.0-1.2.1 (L1), v5.0.0-3.4.3 (L2, CSP)."""

import pytest
from fastapi.testclient import TestClient

from tests.sigurnost.conftest import rezerviraj

pytestmark = pytest.mark.sigurnost

NAPAD = "<script>alert('x')</script><img src=x onerror=alert(1)>"


def test_napomena_se_ispisuje_kodirano_uz_csp(client: TestClient, prijava, novi_termin) -> None:
    ana = prijava("ana")
    nova = rezerviraj(client, ana, novi_termin(1), NAPAD)
    assert nova.status_code == 201

    ispis = client.get(f"/ispis/rezervacije/{nova.json()['id']}", headers=ana)

    assert ispis.status_code == 200
    assert "<script>alert('x')</script>" not in ispis.text
    assert "<img src=x onerror" not in ispis.text
    assert "&lt;script&gt;" in ispis.text
    assert "default-src 'none'" in ispis.headers["content-security-policy"]
