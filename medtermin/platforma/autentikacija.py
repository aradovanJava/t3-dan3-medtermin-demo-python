"""Tokeni prijave i određivanje prijavljenog korisnika.

Token se šalje u zaglavlju ``Authorization: Bearer <token>`` ili u kolačiću ``SESSION`` (prijava obrascem).
Endpoint traži prijavu tako da ima parametar tipa :data:`Prijavljeni`.
"""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from medtermin.platforma.greske import ApiGreska

KOLACIC = "SESSION"


@dataclass(frozen=True)
class PrijavljeniKorisnik:
    id: int
    username: str
    uloga: str

    @property
    def is_admin(self) -> bool:
        return self.uloga == "ADMIN"

    def ima_ulogu(self, *uloge: str) -> bool:
        return self.uloga in uloge


@dataclass
class _Sesija:
    korisnik: PrijavljeniKorisnik
    izdana: float
    zadnja_uporaba: float


class TokenStore:
    """Tokeni prijave čuvaju se u memoriji (token → sesija).

    N-01: token istječe nakon neaktivnosti i najkasnije nakon najduljeg trajanja; odjava ga opoziva, a promjena
    lozinke opoziva sve tokene korisnika.
    """

    def __init__(self, neaktivnost_s: int = 1800, najdulje_s: int = 28800) -> None:
        self._tokeni: dict[str, _Sesija] = {}
        self._brava = threading.Lock()
        self._neaktivnost = neaktivnost_s
        self._najdulje = najdulje_s

    def _istekla(self, sesija: _Sesija, sada: float) -> bool:
        return sada - sesija.zadnja_uporaba > self._neaktivnost or sada - sesija.izdana > self._najdulje

    def izdaj(self, korisnik: PrijavljeniKorisnik) -> str:
        token = secrets.token_urlsafe(32)
        sada = time.monotonic()
        with self._brava:
            for istekli in [t for t, s in self._tokeni.items() if self._istekla(s, sada)]:
                del self._tokeni[istekli]  # čišćenje isteklih
            self._tokeni[token] = _Sesija(korisnik, sada, sada)
        return token

    def korisnik(self, token: str | None) -> PrijavljeniKorisnik | None:
        """Korisnik za valjan token, inače ``None``; istekli token se briše. Upotreba produljuje neaktivnost."""
        if not token:
            return None
        sada = time.monotonic()
        with self._brava:
            sesija = self._tokeni.get(token)
            if sesija is None:
                return None
            if self._istekla(sesija, sada):
                del self._tokeni[token]
                return None
            sesija.zadnja_uporaba = sada
            return sesija.korisnik

    def opozovi(self, token: str | None) -> None:
        """Odjava: token odmah prestaje vrijediti."""
        if token:
            with self._brava:
                self._tokeni.pop(token, None)

    def opozovi_sve(self, username: str) -> None:
        """Promjena lozinke: prestaju vrijediti svi tokeni korisnika."""
        with self._brava:
            for t in [t for t, s in self._tokeni.items() if s.korisnik.username == username]:
                del self._tokeni[t]


def token_iz_zahtjeva(request: Request) -> str | None:
    zaglavlje = request.headers.get("authorization")
    if zaglavlje and zaglavlje[:7].lower() == "bearer ":
        token = zaglavlje[7:].strip()
        return token or None
    kolacic = request.cookies.get(KOLACIC, "").strip()
    return kolacic or None


def prijavljeni_korisnik(request: Request) -> PrijavljeniKorisnik:
    tokeni: TokenStore = request.app.state.kontekst.tokeni
    korisnik = tokeni.korisnik(token_iz_zahtjeva(request))
    if korisnik is None:
        raise ApiGreska(401, "Potrebna je prijava.")
    return korisnik


Prijavljeni = Annotated[PrijavljeniKorisnik, Depends(prijavljeni_korisnik)]
