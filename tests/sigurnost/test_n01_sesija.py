"""N-01 (nalaz s Dana 3): token prijave nije istjecao i nije ga se moglo opozvati.
ASVS v5.0.0-7.4.1 (L1) prekid sesije · 7.3.1 / 7.3.2 (L2) neaktivnost i najdulje trajanje ·
7.4.3 (L2) promjena lozinke prekida druge sesije. Vidi docs/nalazi/N-01-sesija-bez-isteka.md.

Kratka trajanja vrijede samo za ovaj test: varijable okruženja postavljaju se prije stvaranja aplikacije."""

from __future__ import annotations

import re
import time
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from medtermin.app import create_app
from medtermin.postavke import Postavke

pytestmark = pytest.mark.sigurnost

LOZINKA = "Sesija12345!"


@pytest.fixture
def kratka_sesija(monkeypatch, mape) -> Iterator[TestClient]:
    monkeypatch.setenv("APP_SESIJA_NEAKTIVNOST_S", "2")
    monkeypatch.setenv("APP_SESIJA_NAJDULJE_S", "5")
    aplikacija = create_app(Postavke(storage_dir=str(mape.dokumenti), mailbox_dir=str(mape.posta)))
    with TestClient(aplikacija, raise_server_exceptions=False, follow_redirects=False) as klijent:
        yield klijent
    aplikacija.state.baza.zatvori()


def _novi_token(klijent: TestClient, prefiks: str = "sesija") -> tuple[str, dict[str, str]]:
    username = prefiks + str(time.monotonic_ns())[-10:]
    registracija = klijent.post("/api/auth/register", json={
        "username": username, "password": LOZINKA, "email": f"{username}@primjer.hr",
        "ime": "Test", "prezime": "Sesija"})
    assert registracija.status_code == 201, registracija.text
    prijava = klijent.post("/api/auth/login", json={"username": username, "password": LOZINKA})
    assert prijava.status_code == 200
    return username, {"Authorization": f"Bearer {prijava.json()['token']}"}


def test_nakon_odjave_token_vise_ne_vrijedi(kratka_sesija: TestClient) -> None:
    _, zaglavlje = _novi_token(kratka_sesija)
    assert kratka_sesija.get("/api/ja", headers=zaglavlje).status_code == 200

    odjava = kratka_sesija.post("/api/auth/odjava", headers=zaglavlje)

    assert odjava.status_code == 204
    assert kratka_sesija.get("/api/ja", headers=zaglavlje).status_code == 401


def test_token_istjece_nakon_neaktivnosti(kratka_sesija: TestClient) -> None:
    _, zaglavlje = _novi_token(kratka_sesija)
    assert kratka_sesija.get("/api/ja", headers=zaglavlje).status_code == 200

    time.sleep(2.5)

    assert kratka_sesija.get("/api/ja", headers=zaglavlje).status_code == 401


def test_ni_token_u_stalnoj_upotrebi_ne_vrijedi_dulje_od_najduljeg_trajanja(kratka_sesija: TestClient) -> None:
    _, zaglavlje = _novi_token(kratka_sesija)
    for sekunda in range(1, 4):                 # ~3 s: upotreba produljuje neaktivnost
        time.sleep(1)
        assert kratka_sesija.get("/api/ja", headers=zaglavlje).status_code == 200, f"nakon {sekunda} s"
    zadnji = 0
    for _ in range(3):                          # ~6 s: prešli smo najdulje trajanje (5 s)
        time.sleep(1)
        zadnji = kratka_sesija.get("/api/ja", headers=zaglavlje).status_code
    assert zadnji == 401


def test_promjena_lozinke_resetom_prekida_postojece_sesije(kratka_sesija: TestClient, mape) -> None:
    username, stari = _novi_token(kratka_sesija, "reset")
    assert kratka_sesija.post("/api/auth/reset-zahtjev", json={"username": username}).status_code == 202
    poruke = list(mape.posta.glob(f"{username}-*.txt"))
    assert len(poruke) == 1
    token = re.search(r"Token:\s*(\S+)", poruke[0].read_text(encoding="utf-8")).group(1)

    reset = kratka_sesija.post("/api/auth/reset", json={"token": token, "novaLozinka": "NovaSesija12345!"})

    assert reset.status_code == 200
    assert kratka_sesija.get("/api/ja", headers=stari).status_code == 401
