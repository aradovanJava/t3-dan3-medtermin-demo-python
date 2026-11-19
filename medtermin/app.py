"""Tvornica aplikacije: svaki poziv ``create_app()`` dobiva svježu bazu u memoriji i vlastite servise."""

from __future__ import annotations

from importlib import resources

from fastapi import FastAPI

from medtermin import lijecnici, pocetni_podaci
from medtermin.nalazi import api as nalazi_api
from medtermin.platforma import auth_api, greske, postavke_api, prijava
from medtermin.platforma.autentikacija import TokenStore
from medtermin.platforma.baza import Baza
from medtermin.platforma.cors import CorsMiddleware
from medtermin.platforma.kontekst import Kontekst
from medtermin.platforma.korisnici import KorisnikService
from medtermin.platforma.lozinke import LozinkaHasher
from medtermin.platforma.pohrana import Pohrana
from medtermin.platforma.posta import PostaService
from medtermin.platforma.reset_lozinke import ResetLozinkeService
from medtermin.postavke import Postavke
from medtermin.rezervacije import api as rezervacije_api
from medtermin.rezervacije import ispis
from medtermin.rezervacije.bolnicki_sustav import BolnickiSustavKlijent
from medtermin.rezervacije.servis import RezervacijaService
from medtermin.termini import api as termini_api


def create_app(postavke: Postavke | None = None) -> FastAPI:
    postavke = postavke or Postavke()
    baza = Baza()
    baza.skripta(resources.files("medtermin").joinpath("shema.sql").read_text(encoding="utf-8"))
    pohrana = Pohrana(postavke)
    hasher = LozinkaHasher()
    korisnici = KorisnikService(baza, hasher)
    posta = PostaService(pohrana, postavke)
    tokeni = TokenStore(postavke.sesija_neaktivnost_s, postavke.sesija_najdulje_s)
    kontekst = Kontekst(
        postavke=postavke,
        baza=baza,
        pohrana=pohrana,
        tokeni=tokeni,
        hasher=hasher,
        korisnici=korisnici,
        posta=posta,
        reset=ResetLozinkeService(baza, korisnici, posta, tokeni),
        rezervacije=RezervacijaService(baza, BolnickiSustavKlijent()),
    )
    pocetni_podaci.ucitaj(kontekst)

    app = FastAPI(title=postavke.naziv, version="1.0.0")
    app.state.kontekst = kontekst
    app.state.baza = baza
    greske.registriraj(app)
    app.add_middleware(CorsMiddleware, dopusteni_origini=postavke.cors_allowed_origins)
    for router in (
        prijava.router,
        auth_api.router,
        postavke_api.router,
        lijecnici.router,
        termini_api.router,
        rezervacije_api.router,
        ispis.router,
        nalazi_api.router,
    ):
        app.include_router(router)
    return app
