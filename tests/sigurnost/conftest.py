"""Pomoćne funkcije i fixture za sigurnosne testove.

* ``novi_termin(kapacitet)`` – svaki test stvara vlastiti termin (uvoz XML-a kao dr.horvat),
  pa ne ovisi o seed podacima,
* ``posluzitelj`` – **stvarni** uvicorn poslužitelj na slobodnom portu. ``TestClient`` šalje zahtjeve jedan po jedan
  kroz istu petlju događaja, a utrka (S10) nastaje tek kad zahtjevi stvarno idu paralelno.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass

import httpx2 as httpx
import pytest
import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient

from medtermin.app import create_app
from medtermin.postavke import Postavke

OIB = "48291736504"


def uvezi_termin(klijent: TestClient | httpx.Client, zaglavlja: dict[str, str], kapacitet: int) -> int:
    xml = (
        "<termini><termin><lijecnikId>1</lijecnikId><pocetak>2027-03-01T08:00</pocetak>"
        f"<kapacitet>{kapacitet}</kapacitet><napomena>Termin za sigurnosni test</napomena></termin></termini>"
    )
    odgovor = klijent.post("/api/termini/uvoz", content=xml, headers={**zaglavlja, "Content-Type": "application/xml"})
    assert odgovor.status_code == 200, odgovor.text
    return odgovor.json()["termini"][0]["id"]


@pytest.fixture
def novi_termin(client: TestClient, prijava) -> Callable[[int], int]:
    return lambda kapacitet: uvezi_termin(client, prijava("dr.horvat"), kapacitet)


def rezerviraj(klijent: TestClient | httpx.Client, zaglavlja: dict[str, str], termin_id: int, napomena: str):
    return klijent.post(
        "/api/rezervacije", json={"terminId": termin_id, "napomena": napomena, "oib": OIB}, headers=zaglavlja
    )


@dataclass
class Posluzitelj:
    url: str
    app: FastAPI


def _slobodan_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def posluzitelj(mape) -> Iterator[Posluzitelj]:
    aplikacija = create_app(Postavke(storage_dir=str(mape.dokumenti), mailbox_dir=str(mape.posta)))
    port = _slobodan_port()
    server = uvicorn.Server(uvicorn.Config(aplikacija, host="127.0.0.1", port=port, log_level="warning"))
    dretva = threading.Thread(target=server.run, daemon=True)
    dretva.start()
    rok = time.monotonic() + 15
    while not server.started:
        if time.monotonic() > rok:
            raise RuntimeError("uvicorn se nije pokrenuo na vrijeme")
        time.sleep(0.05)
    try:
        yield Posluzitelj(url=f"http://127.0.0.1:{port}", app=aplikacija)
    finally:
        server.should_exit = True
        dretva.join(timeout=10)
        aplikacija.state.baza.zatvori()
