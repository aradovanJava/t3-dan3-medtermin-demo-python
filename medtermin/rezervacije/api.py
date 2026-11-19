"""REST API za rezervacije termina."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response

from medtermin.platforma.autentikacija import Prijavljeni
from medtermin.platforma.greske import ApiGreska
from medtermin.platforma.kontekst import Ctx
from medtermin.rezervacije.servis import NovaRezervacija

router = APIRouter(prefix="/api/rezervacije")


@router.post("", status_code=201)
def kreiraj(zahtjev: NovaRezervacija, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    rezervacija_id = ctx.rezervacije.kreiraj(zahtjev, korisnik)
    rezervacija = ctx.rezervacije.pronadi(rezervacija_id)
    if rezervacija is None:
        raise ApiGreska.nije_pronadeno("Rezervacija nije pronađena.")
    return rezervacija


@router.get("/moje")
def moje(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    return ctx.rezervacije.rezervacije_korisnika(korisnik.username)


@router.delete("/{rezervacija_id}", status_code=204)
def obrisi(rezervacija_id: int, korisnik: Prijavljeni, ctx: Ctx) -> Response:
    ctx.rezervacije.obrisi(rezervacija_id, korisnik)
    return Response(status_code=204)
