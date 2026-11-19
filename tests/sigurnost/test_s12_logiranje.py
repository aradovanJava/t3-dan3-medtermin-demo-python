"""S12 – logiranje (CWE-532, CWE-778). Alat ne čita log i ne zna da je 48291736504 OIB.
ASVS v5.0.0-16.2.5 (L2) osjetljivi podaci u logu · v5.0.0-16.3.1 (L2) zapis neuspjele prijave."""

import logging

import pytest
from fastapi.testclient import TestClient

from tests.sigurnost.conftest import OIB, rezerviraj

pytestmark = pytest.mark.sigurnost


def test_log_bez_tajni_sa_zapisom_neuspjele_prijave(client: TestClient, prijava, novi_termin, caplog) -> None:
    caplog.set_level(logging.INFO, logger="medtermin")
    ana = prijava("ana")
    assert rezerviraj(client, ana, novi_termin(1), "Pregled").status_code == 201
    neuspjela = client.post("/api/auth/login", json={"username": "marko", "password": "pogresna"})
    assert neuspjela.status_code == 401

    assert "Ana12345!" not in caplog.text
    assert OIB not in caplog.text
    assert "*******6504" in caplog.text
    assert any(
        z.levelno == logging.WARNING and "marko" in z.getMessage() for z in caplog.records
    ), "zapis neuspjele prijave za marka na razini WARNING"
