# Model prijetnji – STRIDE po elementu

> Blok 3 radionice. Elementi i ID-jevi su iz [dfd.md](dfd.md). Pravilo: **za svaku prijetnju postojeća kontrola
> (s dokazom) ili ID rizika u [registru](registar-rizika.md)** – prijetnja bez odgovora je nalaz.

STRIDE po elementu (Microsoft SDL): vanjski entitet → S, R · proces → S, T, R, I, D, E · spremište → T, I, D
(+ R za log) · tok podataka → T, I, D. Testovi su u `tests/sigurnost/` i `tests/funkcionalno/`.

| Element | STRIDE | Prijetnja | Postojeća kontrola (dokaz) | Rizik |
|---|---|---|---|---|
| E1 Pacijent | S | Pogađanje lozinke ili credential stuffing (otvorena registracija, nema ograničenja pokušaja) | Argon2id, najmanje 8 znakova, WARNING zapis neuspjele prijave – `test_s12_logiranje.py`; **nema ograničenja broja pokušaja** ([N-02](nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md)) | [R-03](registar-rizika.md#r-03) |
| E1 Pacijent | S | Ukradeni ili ostavljeni token (dijeljeno računalo, log) koristi se danima | istek nakon 30 min neaktivnosti i najkasnije 8 h, odjava, opoziv nakon promjene lozinke – `test_n01_sesija.py` ([N-01](nalazi/N-01-sesija-bez-isteka.md)) | R-01 (zatvoren) |
| E1 Pacijent | R | „Nisam ja otkazao termin“ | zapis otkazivanja s korisnikom (`RezervacijaService.obrisi`) – log nije zaštićen | [R-06](registar-rizika.md#r-06) |
| E2 Liječnik | E | Pacijent poziva uvoz termina | uvoz samo za `LIJECNIK` i `ADMIN` – `test_korisnik_ne_moze_uvoziti_termine` | – |
| E3 Administrator | S | Seed račun `admin` s poznatom lozinkom završi u produkciji | – (`pocetni_podaci.py` puni seed pri svakom pokretanju) | [R-04](registar-rizika.md#r-04) |
| P1 API | E | Brisanje tuđe rezervacije – IDOR (S01) | uvjet vlasnika u servisu – `test_s01_tuda_rezervacija.py` | – |
| P1 API | E | Fail-open: nepoznat format propušta tuđi nalaz (S13) | vlasništvo se provjerava prije formata, 400/404 – `test_s13_fail_open.py` | – |
| P1 API | T | Utrka za zadnje slobodno mjesto (S10) | atomski uvjetni `UPDATE … AND zauzeto < kapacitet` – `test_s10_zadnje_mjesto.py` (stvarni uvicorn, 10 dretvi) | – |
| P1 API | T, I | Pohranjeni XSS na potvrdi za ispis (S09) | `html.escape` + `Content-Security-Policy` – `test_s09_ispis_xss.py` | – |
| P1 API | I | Tekst iznimke ili traceback u odgovoru | rukovatelji u `platforma/greske.py` vraćaju općenitu poruku, traceback samo u logu – `test_s13_fail_open.py` provjerava tijelo | – |
| P1 API | T, E | XXE u uvozu termina (S05) | lxml `resolve_entities=False`, `no_network=True`, DOCTYPE zabranjen; vlastito Semgrep pravilo `python-xxe-lxml-razrjesavanje-entiteta` | – |
| P1 API | T, E | Nesigurna deserijalizacija YAML-a (S06) | `yaml.safe_load`, PyYAML 6.0.3; Semgrep pravilo `python-yaml-load-bez-safeloader` + SCA u vratima (dokaz pada: [PR #11](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/11)) | – |
| P1 API | D | Mnogo zahtjeva, veliko tijelo zahtjeva; Argon2 troši 64 MiB po provjeri lozinke | – | [R-07](registar-rizika.md#r-07) |
| P1 API | I | Swagger UI (`/docs`) i `/openapi.json` bez prijave otkrivaju sve endpointe i sheme (izviđanje) | – (FastAPI ih zadano uključuje) | [R-04](registar-rizika.md#r-04) |
| P1 platforma | T, I, D | Poznata ranjivost u izravnoj ovisnosti (FastAPI, lxml, PyYAML …) | OSV-Scanner i pip-audit u vratima, Dependabot (9 PR-ova, svi prolaze vrata); dokaz pada: [PR #11](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/11) | – |
| D1 Baza | T, I | SQL injection u sortiranju (S08) | rječnik dopuštenih stupaca i smjerova; Semgrep `python-sql-order-by-iz-parametra` + Bandit B608, bez ijedne iznimke | – |
| D1 Baza | I | OIB u čistom tekstu, nešifrirane kopije baze | Dan 2: šifriranje stupca, TDE, šifrirane kopije – još nije primijenjeno u produkciji | [R-09](registar-rizika.md#r-09) |
| D1 Baza | E | Aplikacija se spaja kao `sa` ili `db_owner` | Dan 2: `uloga_aplikacija`, minimalne ovlasti, RLS – još nije primijenjeno u produkciji | [R-09](registar-rizika.md#r-09) |
| D2 Dokumenti nalaza | I | Path traversal kod preuzimanja (S02) | ime datoteke iz baze + `Path.resolve()` i `is_relative_to` – `test_s02_path_traversal.py` | – |
| D3 Log | I | Lozinka i OIB u logu (S12) | lozinka se ne logira, OIB maskiran – `test_s12_logiranje.py` | – |
| D3 Log | R, T | Log se može izmijeniti ili obrisati; nema zapisa tko je čitao nalaz | – | [R-06](registar-rizika.md#r-06) |
| D4 Sesije | D | Ponovno pokretanje poslužitelja odjavljuje sve korisnike | odluka dizajna za jednu instancu ([sigurnosna-pravila.md](sigurnosna-pravila.md#sesija)); uz više uvicorn radnika (`--workers`) ili instanci treba zajedničko spremište | – |
| F1/F2 preglednik ↔ API | I | CORS reflektira bilo koji Origin (S04) | popis origina iz `APP_CORS_ALLOWED_ORIGINS` – `test_s04_cors.py`; ZAP kuka u DAST-u | – |
| F1/F2 preglednik ↔ API | I, T | Promet bez TLS-a; kolačić `SESSION` bez atributa `Secure` | TLS na reverse proxyju – izvan koda aplikacije | [R-08](registar-rizika.md#r-08) |
| F9 e-pošta | S | Predvidljiv ili višekratni token za reset lozinke (S11) | `secrets.token_urlsafe(32)`, u bazi samo SHA-256, 15 min, jednokratan – `test_cijeli_tok_promjene_lozinke`, `test_izmisljeni_token_vraca_400` | – |
| F10 BIS | S, I | Lažni BIS ili presretanje poziva | – (u laboratoriju simulacija) | [R-08](registar-rizika.md#r-08) |
| P2 GitHub Actions | T | Akcija referencirana pomičnom oznakom (`@v5`) – slučaj tj-actions, CVE-2025-30066 | `permissions: contents: read`, Dependabot; **akcije nisu pribijene na SHA** (Semgrep `github-actions-mutable-action-tag`, informativno) | [R-05](registar-rizika.md#r-05) |
| P2 GitHub Actions | I | Tajne u logu pokretanja; `pull_request_target` s kodom iz PR-a | workflow ne koristi `pull_request_target`; tajna samo u poslu DAST; gitleaks na cijeloj povijesti | – |
| D5 Repozitorij | R, T | Force-push na `main`, izmjena bez pregleda | – (zaštita grane ovisi o planu GitHub računa) | [R-05](registar-rizika.md#r-05) |
| E7 Registar paketa | T | Ranjivo ili kompromitirano izdanje **tranzitivne** ovisnosti (npr. Starlette) stiže pri instalaciji – verzija nije zaključana ni provjerena hashom; izmišljen paket (slopsquatting) | SBOM + OSV + pip-audit provjeravaju samo ono što je CI toga dana instalirao; Dependabot s odgodom od 3 dana samo za izravne; pregled PR-a | [R-02](registar-rizika.md#r-02) |

**30 prijetnji · 17 s postojećom kontrolom (uključujući R-01, zatvoren popravkom N-01) · 13 vodi na 8 otvorenih
rizika u registru (R-02 – R-09).**

## Kako je tablica nastala

1. Za svaki element DFD-a postavljena su samo STRIDE pitanja koja se na njegovu vrstu odnose.
2. Za svaku prijetnju potražena je kontrola u kodu ili konfiguraciji i **dokaz** (test, pravilo alata, izvještaj).
   Tvrdnja „imamo validaciju“ bez dokaza nije kontrola.
3. Što nema kontrolu, otišlo je u registar rizika s vlasnikom i rokom.
4. Model se ponovno pregledava kad se promijeni arhitektura (npr. Keycloak, više instanci, nova integracija).
