"""Termini liječnika i uvoz termina iz XML-a."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Query

from medtermin.platforma.autentikacija import Prijavljeni
from medtermin.platforma.greske import ApiGreska
from medtermin.platforma.kontekst import Ctx, SirovoTijelo
from medtermin.termini import uvoz

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/termini")

SELECT = (
    "SELECT t.id, t.lijecnik_id, l.ime, l.prezime, t.pocetak, t.kapacitet, t.zauzeto, t.napomena "
    "FROM termini t JOIN lijecnici l ON l.id = t.lijecnik_id"
)


def _termin(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "lijecnikId": red["lijecnik_id"],
        "lijecnik": f"dr. {red['ime']} {red['prezime']}",
        "pocetak": red["pocetak"],
        "kapacitet": red["kapacitet"],
        "zauzeto": red["zauzeto"],
        "slobodno": red["kapacitet"] - red["zauzeto"],
        "napomena": red["napomena"],
    }


@router.get("")
def popis(
    korisnik: Prijavljeni, ctx: Ctx, lijecnik_id: Annotated[int | None, Query(alias="lijecnikId")] = None
) -> list[dict[str, Any]]:
    """Termini (svi ili jednog liječnika), npr. ``GET /api/termini?lijecnikId=1``."""
    if lijecnik_id is not None:
        redovi = ctx.baza.upit(SELECT + " WHERE t.lijecnik_id = ? ORDER BY t.pocetak, t.id", (lijecnik_id,))
    else:
        redovi = ctx.baza.upit(SELECT + " ORDER BY t.pocetak, t.id")
    return [_termin(red) for red in redovi]


@router.post("/uvoz")
def uvezi(xml: SirovoTijelo, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    """Uvoz termina iz XML-a (liječnik ili administrator)."""
    if not korisnik.ima_ulogu("LIJECNIK", "ADMIN"):
        raise ApiGreska.zabranjeno()
    stavke = uvoz.procitaj(xml)
    for stavka in stavke:
        if ctx.baza.jedan("SELECT id FROM lijecnici WHERE id = ?", (stavka.lijecnik_id,)) is None:
            raise ApiGreska.neispravno(f"Nepoznat liječnik: {stavka.lijecnik_id}")
        if not 1 <= stavka.kapacitet <= 50:
            raise ApiGreska.neispravno("Kapacitet termina mora biti između 1 i 50.")
    uvezeni = []
    with ctx.baza.transakcija() as baza:
        for stavka in stavke:
            pocetak = stavka.pocetak.isoformat(timespec="seconds")
            termin_id = baza.umetni(
                "INSERT INTO termini (lijecnik_id, pocetak, kapacitet, zauzeto, napomena) VALUES (?, ?, ?, 0, ?)",
                (stavka.lijecnik_id, pocetak, stavka.kapacitet, stavka.napomena),
            )
            uvezeni.append({"id": termin_id, "pocetak": pocetak, "napomena": stavka.napomena})
    log.info("Korisnik %s uvezao je %d termina", korisnik.username, len(uvezeni))
    return {"uvezeno": len(uvezeni), "termini": uvezeni}
