"""Popis liječnika, npr. ``GET /api/lijecnici?sort=prezime&smjer=asc``."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from medtermin.platforma.autentikacija import Prijavljeni
from medtermin.platforma.greske import ApiGreska
from medtermin.platforma.kontekst import Ctx

router = APIRouter(prefix="/api/lijecnici")

SELECT_LIJECNICI = "SELECT id, ime, prezime, specijalizacija, ordinacija FROM lijecnici"
STUPCI = {"ime": "ime", "prezime": "prezime", "specijalizacija": "specijalizacija"}
SMJEROVI = {"asc": "ASC", "desc": "DESC"}


@router.get("")
def popis(korisnik: Prijavljeni, ctx: Ctx, sort: str = "prezime", smjer: str = "asc") -> list[dict[str, Any]]:
    stupac = STUPCI.get(sort)
    redoslijed = SMJEROVI.get(smjer.lower())
    if stupac is None or redoslijed is None:
        raise ApiGreska.neispravno("Neispravan parametar sortiranja.")
    sql = f"{SELECT_LIJECNICI} ORDER BY {stupac} {redoslijed}, id"
    return ctx.baza.upit(sql)
