"""Čitanje XML-a s terminima iz rasporeda ordinacije::

    <termini><termin><lijecnikId>1</lijecnikId><pocetak>2026-12-01T09:00</pocetak>
    <kapacitet>1</kapacitet><napomena>Jutarnji termin</napomena></termin></termini>
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from lxml import etree

from medtermin.platforma.greske import ApiGreska


@dataclass(frozen=True)
class Stavka:
    lijecnik_id: int
    pocetak: datetime
    kapacitet: int
    napomena: str | None


def procitaj(xml: bytes) -> list[Stavka]:
    try:
        korijen = _ucitaj(xml)
    except etree.XMLSyntaxError as e:
        raise ApiGreska.neispravno("Neispravan XML.") from e
    stavke: list[Stavka] = []
    for redni_broj, termin in enumerate(korijen.iter("termin"), start=1):
        try:
            stavke.append(
                Stavka(
                    lijecnik_id=int(_tekst(termin, "lijecnikId")),
                    pocetak=datetime.fromisoformat(_tekst(termin, "pocetak")),
                    kapacitet=int(_tekst(termin, "kapacitet")),
                    napomena=_neobavezno(termin, "napomena"),
                )
            )
        except ValueError as e:
            raise ApiGreska.neispravno(f"Neispravni podaci u terminu {redni_broj}.") from e
    return stavke


def _ucitaj(xml: bytes) -> etree._Element:
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    korijen = etree.fromstring(xml, parser)
    # deklaracija tipa dokumenta (DOCTYPE) nije dopuštena
    if korijen.getroottree().docinfo.doctype:
        raise ApiGreska.neispravno("Neispravan XML.")
    return korijen


def _tekst(roditelj: etree._Element, naziv: str) -> str:
    vrijednost = _neobavezno(roditelj, naziv)
    if not vrijednost:
        raise ValueError(f"Nedostaje element {naziv}")
    return vrijednost


def _neobavezno(roditelj: etree._Element, naziv: str) -> str | None:
    element = next(roditelj.iter(naziv), None)
    if element is None:
        return None
    return "".join(element.itertext()).strip()
