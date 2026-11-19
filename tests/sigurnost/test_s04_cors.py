"""S04 – CORS reflektira bilo koji Origin uz credentials (CWE-942). Dopušteni su samo origini iz konfiguracije.
WSTG-CLNT-07 · ASVS v5.0.0-3.4.2 (L1)."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.sigurnost

ZLO = "https://zlo.example"


def test_zahtjev_s_nepoznatog_origina(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/ja", headers={**prijava("ana"), "Origin": ZLO})

    assert odgovor.headers.get("access-control-allow-origin") not in (ZLO, "*")


def test_preflight_s_nepoznatog_origina(client: TestClient) -> None:
    odgovor = client.options("/api/ja", headers={"Origin": ZLO, "Access-Control-Request-Method": "GET"})

    assert odgovor.headers.get("access-control-allow-origin") not in (ZLO, "*")
