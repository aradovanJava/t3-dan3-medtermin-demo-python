"""Servisi jedne instance aplikacije (dostupni endpointima preko ``Depends``)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

from medtermin.platforma.autentikacija import TokenStore
from medtermin.platforma.baza import Baza
from medtermin.platforma.korisnici import KorisnikService
from medtermin.platforma.lozinke import LozinkaHasher
from medtermin.platforma.pohrana import Pohrana
from medtermin.platforma.posta import PostaService
from medtermin.platforma.reset_lozinke import ResetLozinkeService
from medtermin.postavke import Postavke

if TYPE_CHECKING:
    from medtermin.rezervacije.servis import RezervacijaService


@dataclass
class Kontekst:
    postavke: Postavke
    baza: Baza
    pohrana: Pohrana
    tokeni: TokenStore
    hasher: LozinkaHasher
    korisnici: KorisnikService
    posta: PostaService
    reset: ResetLozinkeService
    rezervacije: RezervacijaService


def kontekst(request: Request) -> Kontekst:
    return request.app.state.kontekst


Ctx = Annotated[Kontekst, Depends(kontekst)]


async def _sirovo_tijelo(request: Request) -> bytes:
    return await request.body()


# Tijelo zahtjeva kao bajtovi (XML, YAML)
SirovoTijelo = Annotated[bytes, Depends(_sirovo_tijelo)]
