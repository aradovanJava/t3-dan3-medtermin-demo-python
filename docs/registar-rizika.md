# Registar rizika – MedTermin

> Blok 4 radionice. Ulaz su prijetnje bez kontrole iz [stride.md](stride.md) i nalazi iz
> [nalazi/](nalazi/). Stanje: 19. 11. 2026.

## Ljestvice (dogovor tima, primjenjuju se jednako na sve rizike)

| Razina | Vjerojatnost (V) | Utjecaj (U) |
|---|---|---|
| 1 – niska | treba unutarnji pristup, povlašteni račun ili rijetke uvjete | zanemarivi podaci, bez obveze prijave |
| 2 – srednja | treba posebno znanje, pripremu ili prethodni korak (npr. curenje baze, ukradeni token) | osobni podaci manjeg broja korisnika, kraći prekid rada |
| 3 – visoka | dovoljan je običan korisnik (otvorena registracija), alat ili javni exploit | zdravstveni podaci, OIB; obveza prijave povrede ili incidenta |

**Rizik R = V × U:** 1–2 nizak (prihvatiti uz praćenje) · 3–4 srednji (smanjiti u dogovorenom roku) ·
6–9 visok (smanjiti prije isporuke). Postupanje: izbjeći · smanjiti · prenijeti · prihvatiti.
MedTermin obrađuje zdravstvene podatke (posebna kategorija, GDPR čl. 9), pa je utjecaj za sve što otkriva nalaze ili
rezervacije **3**.

## Registar

| ID | Rizik | V | U | R | Postupanje | Mjera i dokaz | R nakon | Vlasnik · rok | Status |
|---|---|---|---|---|---|---|---|---|---|
| [R-03](#r-03) | Pogađanje lozinke / credential stuffing ([N-02](nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md)) | 3 | 3 | **9** | smanjiti | ograničenje pokušaja po računu i IP-u, provjera lozinke prema popisu čestih lozinki; test „6. pokušaj → 429“ | 3 | voditelj IT-a poliklinike · 15. 12. 2026. | otvoren |
| [R-04](#r-04) | Razvojne značajke u produkciji: seed računi s poznatim lozinkama (`admin`, `dr.horvat`) i Swagger UI (`/docs`, `/openapi.json`) bez prijave | 3 | 3 | **9** | izbjeći | seed i dokumentacija API-ja samo u razvojnom načinu (npr. `APP_RAZVOJ=1`); prvi administrator pri instalaciji; test „bez razvojnog načina nema korisnika admin, a `/docs` vraća 404“ | 3 | voditelj razvoja · prije prve isporuke | otvoren – **blokira isporuku** |
| [R-01](#r-01) | Ukradeni ili ostavljeni token vrijedi zauvijek ([N-01](nalazi/N-01-sesija-bez-isteka.md)) | 2 | 3 | **6** | smanjiti | istek 30 min / 8 h, odjava, opoziv nakon promjene lozinke – `test_n01_sesija.py` ([PR #10](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/10)) | 3 | voditelj IT-a poliklinike · 19. 11. 2026. | **zatvoren** |
| [R-02](#r-02) | Tranzitivne ovisnosti nisu zaključane ni provjerene hashom: CI provjerava jedno, isporuka može dobiti drugo | 2 | 3 | **6** | smanjiti | zaključana datoteka sa svim ovisnostima i hashovima (`pip-compile --generate-hashes` ili `uv pip compile --generate-hashes`), instalacija s `--require-hashes` u CI-ju i u isporuci; Dependabot ažurira zaključanu datoteku | 3 | voditelj razvoja · 31. 1. 2027. | otvoren |
| [R-08](#r-08) | Zaštita prijenosa ovisi o okolini: TLS, HSTS, kolačić `Secure`, TLS prema BIS-u i bazi | 2 | 3 | **6** | prenijeti + smanjiti | ugovor s pružateljem smještaja (TLS 1.2+, HSTS, certifikat); kolačić `__Host-SESSION` sa `Secure` u aplikaciji | 3 | voditelj IT-a poliklinike · prije prve isporuke | otvoren |
| [R-09](#r-09) | Baza u produkciji bez mjera s Dana 2 (OIB u čistom tekstu, preširoke ovlasti, nešifrirane kopije) | 2 | 3 | **6** | smanjiti | skripta iz SQL Server laboratorija; dokaz: izlaz provjere 30/30 i demo „Upozorenja: 0“ | 3 | voditelj razvoja · prije prve isporuke | otvoren |
| [R-06](#r-06) | Log nije zaštićen ni centraliziran; nema zapisa tko je čitao nalaz | 2 | 2 | 4 | smanjiti | zapis pristupa nalazima (tko, koji nalaz, kada – bez sadržaja); log u središnji sustav samo za čitanje | 2 | voditelj razvoja · 31. 1. 2027. | otvoren |
| [R-05](#r-05) | CI/CD: akcije po pomičnoj oznaci (`@v5`), nema zaštite grane `main` | 1 | 3 | 3 | smanjiti, ostatak prihvatiti | akcije pribiti na SHA (Dependabot ih nastavlja ažurirati); zaštita grane kad repozitorij prijeđe na plan koji je podržava | 3 | voditelj razvoja · 30. 11. 2026. | otvoren |
| [R-07](#r-07) | Uskraćivanje usluge: nema ograničenja broja zahtjeva ni veličine tijela; Argon2 troši memoriju po prijavi | 2 | 1 | 2 | prihvatiti | ograničenje na reverse proxyju, praćenje; ponovna procjena | 2 | voditelj IT-a poliklinike · procjena 1. 3. 2027. | prihvaćen |

**Kako čitati:** „R nakon“ je rizik uz uvedenu mjeru. Vjerojatnost pada, utjecaj ostaje – podaci su jednako
vrijedni. Ostane li 6 ili više, mjera nije dovoljna ili vlasnik rizika pisano prihvaća rizik s rokom.
**Prihvaćanje odobrava vlasnik rizika, ne programer.**

## Detalji

### R-01
**Ukradeni ili ostavljeni token vrijedi zauvijek.** Prijetnja: S (E1). Ranjivost: CWE-613 (nalaz N-01 iz ručnog
ispitivanja, WSTG-SESS-06/07). Posljedica: tko dođe do tokena (dijeljeno računalo, log, zaboravljena sesija), čita
nalaze i mijenja rezervacije pacijenta dok se poslužitelj ne pokrene ponovno. V = 2 (treba prvo doći do tokena),
U = 3 (zdravstveni podaci). **Zatvoreno:** [PR #10](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/10), test `test_n01_sesija.py` bio je crven, a sada je zelen.

### R-02
**Nezaključane tranzitivne ovisnosti.** `requirements.txt` pribija 7 izravnih paketa (`fastapi==0.162.0` …), ali
ne i 14 tranzitivnih koje pip bira pri svakoj instalaciji – među njima je **Starlette**, HTTP sloj ispod FastAPI-ja,
te `pydantic_core`, `anyio`, `h11` i `cffi`. Hashova nema, pa se ne provjerava ni je li paket onaj isti koji je CI
vidio. Posljedice: (1) SCA u vratima provjerava verzije koje je pip izabrao **u trenutku pokretanja** – isporuka
sutra može dobiti novu verziju koju nitko nije provjerio; (2) SBOM ne opisuje nužno ono što radi u produkciji
(ASVS 15.1.2); (3) kompromitirano izdanje tranzitivnog paketa na PyPI-ju ulazi bez PR-a i bez odgode od 3 dana
(Dependabot `cooldown` vrijedi samo za ono što je u datoteci). V = 2 (treba ranjivo ili zlonamjerno izdanje u
pravom trenutku), U = 3. Vrata su na `main` zelena – **zeleno nije isto što i ponovljivo**.

### R-03
**Pogađanje lozinke.** Prijetnja: S (E1). Ranjivost: CWE-307 (nalaz N-02, WSTG-ATHN-03). Registracija je otvorena,
lozinka ima najmanje 8 znakova, a broj neuspjelih prijava nije ograničen. Privremeno: svaka neuspjela prijava
zapisuje se kao `WARNING` (dokaz: `test_s12_logiranje.py`) i prati. Mjera: nakon 5 neuspjelih pokušaja u 15 minuta
odgoda za taj račun i IP, odgovor 429; uz to ASVS 6.2.4 (popis čestih lozinki) i dokumentirana pravila (ASVS 6.1.1).

### R-04
**Razvojne značajke u produkciji.** `pocetni_podaci.py` pri svakom pokretanju stvara korisnike s lozinkama iz
`KAKO-POKRENUTI.md` – uključujući administratora; u produkciji je to javno poznata administratorska lozinka
(ASVS 6.3.2). Uz to FastAPI zadano objavljuje Swagger UI na `/docs` i cijelu shemu API-ja na `/openapi.json`, bez
prijave (ASVS 13.4.5) – korisno u razvoju, izviđanje napadaču u produkciji. Postupanje je **izbjeći**: oboje samo u
razvojnom načinu (`FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` izvan njega), prvi administrator pri
instalaciji.

### R-05
**CI/CD.** Workflow ima `permissions: contents: read` (dobro), ali akcije su referencirane oznakom (`@v5`). Oznaku
autor – ili napadač s njegovim računom – može preusmjeriti na drugi commit (tj-actions/changed-files, ožujak 2025.,
CVE-2025-30066, u CISA KEV-u). Semgrep to u svakom pokretanju prijavljuje kao informativno
(`github-actions-mutable-action-tag`). Mjera: puni SHA commita u svakom `uses:`. Zaštita grane `main` za privatni
repozitorij ovisi o planu GitHub računa; dok je nema, vlasnik prihvaća preostali rizik.

### R-06
**Log i revizija.** Log je u konzoli poslužitelja: može se obrisati, nije centraliziran i ne bilježi tko je čitao
koji nalaz – za zdravstvene podatke to je pitanje odgovornosti (GDPR čl. 5(2)) i dokaza kod incidenta.

### R-07
**Uskraćivanje usluge.** Registracija i prijava (Argon2id: oko 64 MiB memorije po izračunu hasha), uvoz XML-a i
parsiranje YAML-a nemaju ograničenja broja zahtjeva ni veličine tijela. Utjecaj je kratki prekid rada (U = 1), pa
vlasnik rizik **prihvaća** uz ograničenje na reverse proxyju i praćenje, s ponovnom procjenom 1. 3. 2027.

### R-08
**Zaštita prijenosa.** TLS, HSTS i certifikat postavlja okolina (reverse proxy ispred uvicorna), ne aplikacija.
Dio rizika se **prenosi** ugovorom na pružatelja smještaja; u aplikaciji ostaje kolačić `SESSION` bez atributa
`Secure` (`set_cookie(..., httponly=True, samesite="lax")`) i poziv BIS-u bez provjerenog TLS-a.

### R-09
**Baza.** Aplikacija u razvoju koristi SQLite u memoriji. U produkciji je SQL Server, a mjere iz laboratorija s
Dana 2 (minimalne ovlasti, RLS, šifriranje OIB-a, TDE, šifrirane kopije) moraju biti primijenjene **prije**
isporuke – dokaz je izlaz automatske provjere (30/30 PROŠLO).
