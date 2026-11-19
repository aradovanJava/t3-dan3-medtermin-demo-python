"""S13 – fail-open (CWE-636, CWE-209). Iznimka nastaje samo na rubnom ulazu koji skener ne šalje.
WSTG-ERRH-01, WSTG-ATHZ-02 · ASVS v5.0.0-16.5.3 (L2)."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.sigurnost


@pytest.mark.parametrize("format_", ["xml", ""])
def test_tudi_nalaz_s_nepoznatim_formatom(client: TestClient, prijava, format_: str) -> None:
    odgovor = client.get("/api/nalazi/1", params={"format": format_}, headers=prijava("marko"))

    assert odgovor.status_code in (400, 403, 404)
    assert "Krvna slika" not in odgovor.text
    assert "Traceback" not in odgovor.text
    assert "Error" not in odgovor.text
