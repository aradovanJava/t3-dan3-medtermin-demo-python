"""REST API: stanje sustava, prijava, registracija, zaboravljena lozinka i podaci prijavljenog korisnika."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from medtermin.platforma.autentikacija import KOLACIC, Prijavljeni, token_iz_zahtjeva
from medtermin.platforma.greske import ApiGreska, greska
from medtermin.platforma.kontekst import Ctx
from medtermin.platforma.korisnici import PrijavaZahtjev, RegistracijaZahtjev

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class ResetZahtjev(BaseModel):
    username: str | None = None


class NovaLozinka(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str | None = None
    nova_lozinka: str | None = Field(default=None, alias="novaLozinka")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@router.post("/auth/login")
def login(zahtjev: PrijavaZahtjev, ctx: Ctx) -> JSONResponse:
    korisnik = ctx.korisnici.prijava(zahtjev)
    if korisnik is None:
        return greska(401, "Neispravno korisničko ime ili lozinka.")
    token = ctx.tokeni.izdaj(korisnik.prijavljeni())
    return JSONResponse({"token": token, "username": korisnik.username, "uloga": korisnik.uloga})


@router.post("/auth/odjava", status_code=204)
def odjava(request: Request, korisnik: Prijavljeni, ctx: Ctx) -> Response:
    """N-01: odjava opoziva token (zaglavlje ili kolačić) i briše kolačić SESSION."""
    ctx.tokeni.opozovi(token_iz_zahtjeva(request))
    log.info("Odjava korisnika %s", korisnik.username)
    odgovor = Response(status_code=204)
    odgovor.delete_cookie(KOLACIC, path="/", httponly=True, samesite="lax")
    return odgovor


@router.post("/auth/register", status_code=201)
def register(zahtjev: RegistracijaZahtjev, ctx: Ctx) -> dict[str, object]:
    korisnik = ctx.korisnici.registriraj(zahtjev)
    return {"id": korisnik.id, "username": korisnik.username}


@router.post("/auth/reset-zahtjev", status_code=202)
def reset_zahtjev(zahtjev: ResetZahtjev, ctx: Ctx) -> dict[str, str]:
    if zahtjev.username and zahtjev.username.strip():
        ctx.reset.zatrazi(zahtjev.username.strip())
    return {"poruka": "Ako korisnik postoji, poslali smo upute na e-mail."}


@router.post("/auth/reset")
def reset(zahtjev: NovaLozinka, ctx: Ctx) -> dict[str, str]:
    if not ctx.reset.postavi_novu_lozinku(zahtjev.token, zahtjev.nova_lozinka):
        raise ApiGreska.neispravno("Token nije valjan ili je istekao.")
    return {"poruka": "Lozinka je promijenjena."}


@router.get("/ja")
def ja(korisnik: Prijavljeni, ctx: Ctx) -> dict[str, object]:
    podaci = ctx.korisnici.pronadi(korisnik.username)
    if podaci is None:
        raise ApiGreska(401, "Potrebna je prijava.")
    return {
        "username": podaci.username,
        "ime": podaci.ime,
        "prezime": podaci.prezime,
        "email": podaci.email,
        "uloga": podaci.uloga,
    }
