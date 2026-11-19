"""S10 – utrka kod zadnjeg slobodnog mjesta (CWE-362). Pojedinačni zahtjev je uvijek ispravan; greška postoji samo
kad stigne više zahtjeva istodobno – zato je nijedan alat iz pipelinea ne vidi. WSTG-BUSL-05 · ASVS v5.0.0-2.3.4 (L2).

Bitno: stvarni poslužitelj (fixture ``posluzitelj`` – TestClient ne pomaže), barijera da svi zahtjevi krenu zajedno
i provjera da je TOČNO jedan uspio."""

import threading
import uuid

import httpx2 as httpx
import pytest

from tests.conftest import LOZINKE
from tests.sigurnost.conftest import rezerviraj, uvezi_termin

pytestmark = pytest.mark.sigurnost

KORISNIKA = 10
LOZINKA = "Lozinka12345!"


def _token(klijent: httpx.Client, username: str, lozinka: str) -> str:
    odgovor = klijent.post("/api/auth/login", json={"username": username, "password": lozinka})
    assert odgovor.status_code == 200, odgovor.text
    return odgovor.json()["token"]


def test_samo_jedan_dobiva_zadnje_mjesto(posluzitelj) -> None:
    with httpx.Client(base_url=posluzitelj.url, timeout=30) as klijent:
        lijecnik = {"Authorization": f"Bearer {_token(klijent, 'dr.horvat', LOZINKE['dr.horvat'])}"}
        termin = uvezi_termin(klijent, lijecnik, kapacitet=1)
        tokeni = []
        for _ in range(KORISNIKA):
            username = "utrka" + uuid.uuid4().hex[:10]
            registracija = klijent.post("/api/auth/register", json={
                "username": username, "password": LOZINKA, "email": f"{username}@primjer.hr",
                "ime": "Test", "prezime": "Utrka"})
            assert registracija.status_code == 201, registracija.text
            tokeni.append(_token(klijent, username, LOZINKA))

    start = threading.Barrier(KORISNIKA)
    kodovi: list[int] = []
    brava = threading.Lock()

    def posalji(token: str) -> None:
        with httpx.Client(base_url=posluzitelj.url, timeout=60) as k:
            start.wait(timeout=20)                      # svi kreću zajedno
            odgovor = rezerviraj(k, {"Authorization": f"Bearer {token}"}, termin, "Utrka")
        with brava:
            kodovi.append(odgovor.status_code)

    dretve = [threading.Thread(target=posalji, args=(t,)) for t in tokeni]
    for d in dretve:
        d.start()
    for d in dretve:
        d.join(timeout=90)

    assert sorted(kodovi) == [201] + [409] * (KORISNIKA - 1), f"kodovi odgovora: {sorted(kodovi)}"
    red = posluzitelj.app.state.baza.jedan("SELECT kapacitet, zauzeto FROM termini WHERE id = ?", (termin,))
    assert red["zauzeto"] == red["kapacitet"], "slobodnih mjesta nakon utrke mora biti 0"
