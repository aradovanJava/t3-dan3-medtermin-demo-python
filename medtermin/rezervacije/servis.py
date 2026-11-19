"""Rezervacije termina: stvaranje, pregled i otkazivanje."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from medtermin.platforma.autentikacija import PrijavljeniKorisnik
from medtermin.platforma.baza import Baza
from medtermin.platforma.greske import ApiGreska
from medtermin.rezervacije.bolnicki_sustav import BolnickiSustavKlijent

log = logging.getLogger(__name__)

OIB = re.compile(r"\d{11}")

SELECT = (
    "SELECT r.id, r.termin_id, r.pacijent, r.napomena, r.kreirano, t.pocetak, l.ime, l.prezime "
    "FROM rezervacije r JOIN termini t ON t.id = r.termin_id JOIN lijecnici l ON l.id = t.lijecnik_id"
)


class NovaRezervacija(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    termin_id: int | None = Field(default=None, alias="terminId")
    napomena: str | None = None
    oib: str | None = None


def _rezervacija(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "terminId": red["termin_id"],
        "pacijent": red["pacijent"],
        "lijecnik": f"dr. {red['ime']} {red['prezime']}",
        "pocetak": red["pocetak"],
        "napomena": red["napomena"],
        "kreirano": red["kreirano"],
    }


class RezervacijaService:
    def __init__(self, baza: Baza, bis: BolnickiSustavKlijent) -> None:
        self._baza = baza
        self._bis = bis

    def pronadi(self, rezervacija_id: int) -> dict[str, Any] | None:
        red = self._baza.jedan(SELECT + " WHERE r.id = ?", (rezervacija_id,))
        return _rezervacija(red) if red else None

    def rezervacije_korisnika(self, username: str) -> list[dict[str, Any]]:
        redovi = self._baza.upit(SELECT + " WHERE r.pacijent = ? ORDER BY t.pocetak, r.id", (username,))
        return [_rezervacija(red) for red in redovi]

    def kreiraj(self, zahtjev: NovaRezervacija, korisnik: PrijavljeniKorisnik) -> int:
        if zahtjev.termin_id is None:
            raise ApiGreska.neispravno("Termin je obavezan.")
        if zahtjev.oib is None or not OIB.fullmatch(zahtjev.oib):
            raise ApiGreska.neispravno("OIB mora imati 11 znamenki.")
        if zahtjev.napomena is not None and len(zahtjev.napomena) > 1000:
            raise ApiGreska.neispravno("Napomena smije imati najviše 1000 znakova.")
        termin_id = zahtjev.termin_id
        if self._baza.jedan("SELECT id FROM termini WHERE id = ?", (termin_id,)) is None:
            raise ApiGreska.nije_pronadeno("Termin nije pronađen.")
        log.info(
            "Nova rezervacija: termin %s, korisnik %s, OIB %s", termin_id, korisnik.username, maskiraj_oib(zahtjev.oib)
        )
        azurirano = self._baza.izvrsi(
            "UPDATE termini SET zauzeto = zauzeto + 1 WHERE id = ? AND zauzeto < kapacitet", (termin_id,)
        )
        if azurirano == 0:
            raise ApiGreska(409, "Nema slobodnih mjesta.")
        try:
            oznaka = self._bis.upisi_u_raspored(termin_id, korisnik.username)
            return self._spremi(zahtjev, korisnik, oznaka)
        except Exception:
            self._baza.izvrsi("UPDATE termini SET zauzeto = zauzeto - 1 WHERE id = ?", (termin_id,))
            raise

    def obrisi(self, rezervacija_id: int, korisnik: PrijavljeniKorisnik) -> None:
        rezervacija = self.pronadi(rezervacija_id)
        if rezervacija is None or not (korisnik.is_admin or rezervacija["pacijent"] == korisnik.username):
            raise ApiGreska.nije_pronadeno("Rezervacija nije pronađena.")
        with self._baza.transakcija() as baza:
            baza.izvrsi("DELETE FROM rezervacije WHERE id = ?", (rezervacija["id"],))
            baza.izvrsi(
                "UPDATE termini SET zauzeto = zauzeto - 1 WHERE id = ? AND zauzeto > 0", (rezervacija["terminId"],)
            )
        log.info("Rezervacija %s je otkazana (korisnik %s)", rezervacija_id, korisnik.username)

    def _spremi(self, zahtjev: NovaRezervacija, korisnik: PrijavljeniKorisnik, oznaka_bis: str) -> int:
        return self._baza.umetni(
            "INSERT INTO rezervacije (termin_id, pacijent, napomena, oib, kreirano, oznaka_bis) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                zahtjev.termin_id,
                korisnik.username,
                zahtjev.napomena,
                zahtjev.oib,
                datetime.now().isoformat(timespec="seconds"),
                oznaka_bis,
            ),
        )


def maskiraj_oib(oib: str | None) -> str:
    if oib is None or len(oib) < 4:
        return "***"
    return "*" * (len(oib) - 4) + oib[-4:]
