"""Početni podaci (baza je u memoriji pa se puni pri svakom pokretanju).

Lozinke se spremaju istom metodom kao pri registraciji.
"""

from __future__ import annotations

import logging
from datetime import datetime

from medtermin.platforma.kontekst import Kontekst

log = logging.getLogger(__name__)

NALAZ_ANA = """Poliklinika MedTermin – laboratorijski nalaz
Pacijent: Ana Anić
Pretraga: kompletna krvna slika
Leukociti: 6,4 x10^9/L (referentno 3,4 – 9,7)
Eritrociti: 4,62 x10^12/L (referentno 3,86 – 5,08)
Hemoglobin: 138 g/L (referentno 119 – 157)
Trombociti: 245 x10^9/L (referentno 158 – 424)
Zaključak: nalaz unutar referentnih vrijednosti.
"""

NALAZ_MARKO = """Poliklinika MedTermin – radiološki nalaz
Pacijent: Marko Marić
Pretraga: RTG lumbalne kralježnice u dva smjera
Nalaz: blago smanjena visina intervertebralnog prostora L4-L5, bez znakova prijeloma.
Preporuka: fizikalna terapija i kontrola za tri mjeseca.
"""

LIJECNICI = [
    ("Ivan", "Horvat", "Kardiologija", "Ordinacija 1"),
    ("Maja", "Kovačević", "Dermatologija", "Ordinacija 2"),
    ("Tomislav", "Babić", "Ortopedija", "Ordinacija 3"),
    ("Petra", "Novak", "Neurologija", "Ordinacija 4"),
    ("Luka", "Jurić", "Interna medicina", "Ordinacija 5"),
    ("Ema", "Vuković", "Oftalmologija", "Ordinacija 6"),
]

# (lijecnik_id, pocetak, kapacitet, zauzeto) – id 1–10
TERMINI = [
    (1, "2026-12-01T08:00:00", 1, 1),
    (2, "2026-12-01T09:00:00", 1, 1),
    (1, "2026-12-01T09:00:00", 1, 0),
    (2, "2026-12-01T10:00:00", 1, 0),
    (3, "2026-12-02T08:00:00", 1, 0),
    (4, "2026-12-02T09:00:00", 1, 0),
    (5, "2026-12-02T10:00:00", 1, 0),
    (6, "2026-12-03T08:00:00", 1, 0),
    (1, "2026-12-03T09:00:00", 3, 0),
    (3, "2026-12-03T10:00:00", 1, 0),
]


def ucitaj(ctx: Kontekst) -> None:
    ctx.pohrana.pripremi()
    ctx.pohrana.zapisi_ako_ne_postoji("nalaz-ana-krvna-slika.txt", NALAZ_ANA)
    ctx.pohrana.zapisi_ako_ne_postoji("nalaz-marko-rtg.txt", NALAZ_MARKO)

    korisnici = ctx.korisnici
    korisnici.kreiraj("ana", "Ana12345!", "ana@primjer.hr", "Ana", "Anić", "KORISNIK", "48291736504")
    korisnici.kreiraj("marko", "Marko12345!", "marko@primjer.hr", "Marko", "Marić", "KORISNIK", "73019485267")
    korisnici.kreiraj(
        "dr.horvat", "Ovlasteni12345!", "dr.horvat@primjer.hr", "Ivan", "Horvat", "LIJECNIK", "50617283940"
    )
    korisnici.kreiraj("admin", "Admin12345!", "admin@primjer.hr", "Ivana", "Admin", "ADMIN", "61728394051")

    baza = ctx.baza
    with baza.transakcija():
        for lijecnik in LIJECNICI:
            baza.izvrsi(
                "INSERT INTO lijecnici (ime, prezime, specijalizacija, ordinacija) VALUES (?, ?, ?, ?)", lijecnik
            )
        for termin in TERMINI:
            baza.izvrsi("INSERT INTO termini (lijecnik_id, pocetak, kapacitet, zauzeto) VALUES (?, ?, ?, ?)", termin)
        sada = datetime.now().isoformat(timespec="seconds")
        for rezervacija in [
            (1, "ana", "Kontrolni pregled tlaka", "48291736504", sada, "BIS-1-1000"),
            (2, "marko", "Bolovi u leđima", "73019485267", sada, "BIS-2-1000"),
        ]:
            baza.izvrsi(
                "INSERT INTO rezervacije (termin_id, pacijent, napomena, oib, kreirano, oznaka_bis) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                rezervacija,
            )
        baza.izvrsi(
            "INSERT INTO nalazi (pacijent, naziv, datoteka) VALUES (?, ?, ?)",
            ("ana", "Krvna slika", "nalaz-ana-krvna-slika.txt"),
        )
        baza.izvrsi(
            "INSERT INTO nalazi (pacijent, naziv, datoteka) VALUES (?, ?, ?)",
            ("marko", "RTG kralježnice", "nalaz-marko-rtg.txt"),
        )
    log.info("Početni podaci su učitani")
