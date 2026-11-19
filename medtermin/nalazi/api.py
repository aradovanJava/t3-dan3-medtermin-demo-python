"""Nalazi pacijenata: popis, prikaz (JSON ili PDF) i preuzimanje datoteke nalaza."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Annotated, Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from medtermin.nalazi import pdf
from medtermin.platforma.autentikacija import Prijavljeni
from medtermin.platforma.greske import ApiGreska
from medtermin.platforma.kontekst import Ctx, Kontekst

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nalazi")


class Format(Enum):
    JSON = "json"
    PDF = "pdf"

    @classmethod
    def procitaj(cls, vrijednost: str) -> Format | None:
        return next((f for f in cls if f.value == vrijednost.strip().lower()), None)


@router.get("/moji")
def moji(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    return ctx.baza.upit(
        "SELECT id, pacijent, naziv, datoteka FROM nalazi WHERE pacijent = ? ORDER BY id", (korisnik.username,)
    )


@router.get("/preuzmi")
def preuzmi(datoteka: str, korisnik: Prijavljeni, ctx: Ctx) -> Response:
    """Preuzimanje datoteke nalaza: ``GET /api/nalazi/preuzmi?datoteka=nalaz-ana-krvna-slika.txt``."""
    nalazi = ctx.baza.upit("SELECT id, pacijent, naziv, datoteka FROM nalazi WHERE datoteka = ?", (datoteka,))
    nalaz = next((n for n in nalazi if korisnik.is_admin or n["pacijent"] == korisnik.username), None)
    if nalaz is None:
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    korijen = ctx.pohrana.dokumenti.resolve()
    putanja = (korijen / nalaz["datoteka"]).resolve()
    if not putanja.is_relative_to(korijen):
        raise ApiGreska.neispravno("Neispravan naziv datoteke.")
    if not putanja.is_file():
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    return Response(
        content=putanja.read_bytes(),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{putanja.name}"'},
    )


@router.get("/{nalaz_id}")
def nalaz(
    nalaz_id: int,
    korisnik: Prijavljeni,
    ctx: Ctx,
    oblik: Annotated[str | None, Query(alias="format")] = None,
) -> Response:
    """Nalaz u JSON obliku (metapodaci i sadržaj) ili kao PDF: ``GET /api/nalazi/1?format=pdf``."""
    n = ctx.baza.jedan("SELECT id, pacijent, naziv, datoteka FROM nalazi WHERE id = ?", (nalaz_id,))
    if n is None:
        raise ApiGreska.nije_pronadeno("Nalaz nije pronađen.")
    trazeni = "json" if oblik is None else oblik
    if not korisnik.is_admin and n["pacijent"] != korisnik.username:
        raise ApiGreska.nije_pronadeno("Nalaz nije pronađen.")
    odabrani = Format.procitaj(trazeni)
    if odabrani is None:
        raise ApiGreska.neispravno("Nepodržan format. Dopušteno: json, pdf.")
    return _prikazi(ctx, n, odabrani, None)


def _prikazi(ctx: Kontekst, n: dict[str, Any], odabrani: Format, napomena: str | None) -> Response:
    datoteka = ctx.pohrana.dokumenti / n["datoteka"]
    if not datoteka.is_file():
        raise ApiGreska.nije_pronadeno("Datoteka nalaza nije pronađena.")
    sadrzaj = datoteka.read_text(encoding="utf-8")
    if odabrani is Format.PDF:
        return Response(
            content=pdf.izradi(f"Nalaz: {n['naziv']}", sadrzaj.splitlines()),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="nalaz-{n["id"]}.pdf"'},
        )
    tijelo = {**n, "sadrzaj": sadrzaj}
    if napomena is not None:
        tijelo["napomena"] = napomena
    return JSONResponse(tijelo)
