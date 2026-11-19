"""Potvrda rezervacije za ispis (HTML)."""

from __future__ import annotations

from datetime import datetime
from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from medtermin.platforma.autentikacija import Prijavljeni
from medtermin.platforma.greske import ApiGreska
from medtermin.platforma.kontekst import Ctx

router = APIRouter()


@router.get("/ispis/rezervacije/{rezervacija_id}", response_class=HTMLResponse)
def potvrda(rezervacija_id: int, korisnik: Prijavljeni, ctx: Ctx) -> HTMLResponse:
    r = ctx.rezervacije.pronadi(rezervacija_id)
    if r is None or not (korisnik.is_admin or r["pacijent"] == korisnik.username):
        raise ApiGreska.nije_pronadeno("Rezervacija nije pronađena.")
    termin = datetime.fromisoformat(r["pocetak"]).strftime("%d.%m.%Y. u %H:%M") if r["pocetak"] else ""
    sadrzaj = f"""<!DOCTYPE html>
<html lang="hr">
<head>
<meta charset="UTF-8">
<title>Potvrda rezervacije br. {r["id"]}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; }}
dt {{ font-weight: bold; margin-top: .5rem; }}
</style>
</head>
<body>
<h1>{_tekst(ctx.postavke.naziv)}</h1>
<h2>Potvrda rezervacije br. {r["id"]}</h2>
<dl>
<dt>Pacijent</dt><dd>{_tekst(r["pacijent"])}</dd>
<dt>Liječnik</dt><dd>{_tekst(r["lijecnik"])}</dd>
<dt>Termin</dt><dd>{termin}</dd>
<dt>Napomena</dt><dd>{_tekst(r["napomena"])}</dd>
</dl>
<p>Molimo dođite 10 minuta prije termina i ponesite iskaznicu zdravstvenog osiguranja.</p>
</body>
</html>
"""
    odgovor = HTMLResponse(content=sadrzaj)
    odgovor.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    return odgovor


def _tekst(vrijednost: str | None) -> str:
    return "" if vrijednost is None else escape(vrijednost)
