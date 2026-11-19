"""Zaboravljena lozinka: token se šalje e-poštom, a njime se postavlja nova lozinka."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from medtermin.platforma.autentikacija import TokenStore
from medtermin.platforma.baza import Baza
from medtermin.platforma.korisnici import KorisnikService, provjeri_lozinku
from medtermin.platforma.posta import PostaService

TRAJANJE_TOKENA = timedelta(minutes=15)


class ResetLozinkeService:
    def __init__(self, baza: Baza, korisnici: KorisnikService, posta: PostaService, tokeni: TokenStore) -> None:
        self._baza = baza
        self._korisnici = korisnici
        self._posta = posta
        self._tokeni = tokeni

    def zatrazi(self, username: str) -> None:
        korisnik = self._korisnici.pronadi(username)
        if korisnik is None:
            return
        token = secrets.token_urlsafe(32)
        istjece = (datetime.now() + TRAJANJE_TOKENA).isoformat(timespec="seconds")
        self._baza.izvrsi(
            "INSERT INTO reset_tokeni (username, token, istjece) VALUES (?, ?, ?)",
            (username, _sazetak(token), istjece),
        )
        self._posta.posalji_upute_za_lozinku(korisnik, token)

    def postavi_novu_lozinku(self, token: str | None, nova_lozinka: str | None) -> bool:
        provjeri_lozinku(nova_lozinka)
        if token is None or not token.strip():
            return False
        sada = datetime.now().isoformat(timespec="seconds")
        zapis = self._baza.jedan(
            "SELECT id, username FROM reset_tokeni WHERE token = ? AND iskoristen = 0 AND istjece > ?",
            (_sazetak(token.strip()), sada),
        )
        if zapis is None:
            return False
        iskoristeno = self._baza.izvrsi(
            "UPDATE reset_tokeni SET iskoristen = 1 WHERE id = ? AND iskoristen = 0", (zapis["id"],)
        )
        if iskoristeno != 1:
            return False
        self._korisnici.promijeni_lozinku(zapis["username"], nova_lozinka)
        self._tokeni.opozovi_sve(zapis["username"])  # N-01: stari (možda ukradeni) tokeni više ne vrijede
        return True


def _sazetak(vrijednost: str) -> str:
    return hashlib.sha256(vrijednost.encode("utf-8")).hexdigest()
