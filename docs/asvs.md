# ASVS 5.0.0 lista s dokazima – MedTermin (Python)

> Blok 5 radionice. Svi L1 zahtjevi (70) i odabrani L2 zahtjevi. Izvor ID-jeva: OWASP ASVS 5.0.0
> (CSV iz repozitorija OWASP/ASVS, oznaka v5.0.0). ID se navodi s verzijom (v5.0.0-8.2.2) jer se brojevi mijenjaju
> između verzija. Stanje: 19. 11. 2026., commit na `main`.

**L1:** 33 ✅ ispunjeno · 12 ⚠️ djelomično · 7 ❌ nije ispunjeno · 18 ➖ ne odnosi se (s razlogom).  
**L2 (odabrano):** 10 ✅ · 2 ⚠️ · 2 ❌.

Valjan dokaz je, od najjačeg prema slabijem: **test** (crven na ranjivom kodu, zelen nakon popravka) · **izvještaj
alata** s datumom i commitom (Summary vrata, SARIF, SBOM, ZAP) · **konfiguracija ili kod** (poveznica na redak) ·
**stanje baze** (izlaz provjere iz laboratorija s Dana 2). „Implementirano“ nije dokaz.

Svaki ❌ i ⚠️ ima rizik u [registru](registar-rizika.md) ili je otvorena stavka. Testovi su u
`tests/sigurnost/` i u `tests/funkcionalno/` (`pytest -m sigurnost`, `pytest -m funkcionalno`).

## Razina L1

### V1 Encoding and Sanitization

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-1.2.1 | Kodiranje izlaza prema kontekstu (HTML …) | ✅ | `tests/sigurnost/test_s09_ispis_xss.py` (S09); `html.escape` u `medtermin/rezervacije/ispis.py` |
| v5.0.0-1.2.2 | Kodiranje nepouzdanih podataka u URL-ovima, samo sigurni protokoli | ✅ | `returnUrl` samo lokalni put – `tests/sigurnost/test_s03_open_redirect.py` (S03); token u poveznici base64url |
| v5.0.0-1.2.3 | Kodiranje kod generiranja JavaScripta/JSON-a | ✅ | JSON isključivo preko FastAPI-ja / pydantica, nema ručnog sastavljanja |
| v5.0.0-1.2.4 | Parametrizirani upiti (SQL injection) | ✅ | svi upiti s `?` (sqlite3); ORDER BY iz rječnika dopuštenih (S08) – Semgrep (vlastito pravilo) + Bandit B608 u vratima |
| v5.0.0-1.2.5 | Zaštita od OS command injectiona | ➖ | aplikacija ne poziva naredbe operacijskog sustava |
| v5.0.0-1.3.1 | Sanitizacija HTML-a iz WYSIWYG uređivača | ➖ | nema unosa HTML-a; napomena se kodira (1.2.1) |
| v5.0.0-1.3.2 | Bez eval()/exec() nad korisničkim unosom | ✅ | nema dinamičkog izvođenja koda (Bandit B307 u vratima) |
| v5.0.0-1.5.1 | XML parser bez vanjskih entiteta (XXE) | ✅ | lxml `XMLParser(resolve_entities=False, no_network=True)`, DOCTYPE zabranjen (S05); vlastito Semgrep pravilo za regresiju |

### V2 Validation and Business Logic

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-2.1.1 | Dokumentirana pravila provjere ulaza | ✅ | [sigurnosna-pravila.md](sigurnosna-pravila.md#provjera-ulaza-asvs-211) |
| v5.0.0-2.2.1 | Provjera ulaza prema poslovnim očekivanjima (allowlist) | ✅ | OIB, duljina napomene, `sort`, `format` – vidi 2.1.1 |
| v5.0.0-2.2.2 | Provjera na pouzdanom sloju (poslužitelj) | ✅ | sve provjere u servisima i rukovateljima ruta na poslužitelju |
| v5.0.0-2.3.1 | Poslovni tok samo u očekivanom redoslijedu koraka | ✅ | reset lozinke: zahtjev → jednokratni token → nova lozinka |

### V3 Web Frontend Security

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-3.2.1 | Preglednik ne smije prikazati sadržaj u krivom kontekstu | ⚠️ | ispravan `Content-Type`, preuzimanje nalaza s `Content-Disposition: attachment`; nema `X-Content-Type-Options: nosniff` (ZAP 10021, informativno) |
| v5.0.0-3.2.2 | Siguran prikaz teksta u klijentu (textContent …) | ➖ | nema klijentskog JavaScripta; HTML se generira na poslužitelju i kodira |
| v5.0.0-3.3.1 | Kolačić s atributom Secure i prefiksom __Host-/__Secure- | ❌ | kolačić `SESSION` bez `Secure` i bez prefiksa – [R-08](registar-rizika.md#r-08) |
| v5.0.0-3.4.1 | HSTS na svim odgovorima | ⚠️ | postavlja reverse proxy u produkciji, ne aplikacija – [R-08](registar-rizika.md#r-08) |
| v5.0.0-3.4.2 | CORS samo za dopuštene origine | ✅ | popis iz `APP_CORS_ALLOWED_ORIGINS` – `tests/sigurnost/test_s04_cors.py` (S04); ZAP kuka u DAST-u |
| v5.0.0-3.5.1 | Zaštita od zahtjeva s druge domene (CSRF) bez oslanjanja na preflight | ⚠️ | API traži token u zaglavlju; kolačić `SESSION` ima `SameSite=Lax`, ali nema provjere `Origin`/`Sec-Fetch-Site` |
| v5.0.0-3.5.2 | Osjetljiva funkcija ne smije biti dostupna „jednostavnim“ zahtjevom | ⚠️ | JSON tijelo traži preflight; uz kolačić vrijedi napomena kod 3.5.1 |
| v5.0.0-3.5.3 | Osjetljive radnje samo POST/PUT/DELETE, ne GET | ✅ | promjene stanja samo kroz POST i DELETE |

### V4 API and Web Service

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-4.1.1 | Content-Type s charsetom odgovara sadržaju | ⚠️ | HTML `text/html; charset=utf-8`; JSON `application/json` bez charseta (UTF-8 po RFC 8259) |
| v5.0.0-4.4.1 | WebSocket samo preko WSS-a | ➖ | nema WebSocketa |

### V5 File Handling

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-5.2.1 | Ograničena veličina datoteka koje aplikacija prima | ❌ | tijelo uvoza XML-a i YAML-a nema ograničenja – [R-07](registar-rizika.md#r-07) |
| v5.0.0-5.2.2 | Provjera ekstenzije i sadržaja prenesenih datoteka | ➖ | nema prijenosa datoteka (XML/YAML stižu kao tijelo zahtjeva – 1.5.1) |
| v5.0.0-5.3.1 | Generirane datoteke se ne izvode kao kod | ✅ | dokumenti su u `APP_STORAGE_DIR`; aplikacija ne poslužuje statičke datoteke |
| v5.0.0-5.3.2 | Putanje iz pouzdanih podataka, ne iz korisnikova imena datoteke | ✅ | ime iz baze + `Path.resolve()` i `is_relative_to` – `tests/sigurnost/test_s02_path_traversal.py` (S02) |

### V6 Authentication

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-6.1.1 | Dokumentirana zaštita od pogađanja lozinke | ❌ | pravilo još ne postoji – [N-02](nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md), [R-03](registar-rizika.md#r-03) |
| v5.0.0-6.2.1 | Lozinka najmanje 8 znakova | ✅ | `MIN_DULJINA_LOZINKE = 8` u `medtermin/platforma/korisnici.py` |
| v5.0.0-6.2.2 | Korisnik može promijeniti lozinku | ⚠️ | samo resetom preko e-pošte; nema promjene iz prijavljenog računa |
| v5.0.0-6.2.3 | Promjena lozinke traži trenutnu i novu lozinku | ❌ | funkcija ne postoji (vidi 6.2.2) – otvorena stavka |
| v5.0.0-6.2.4 | Provjera nove lozinke prema popisu ≥ 3000 čestih | ❌ | ne postoji – dio mjere za [R-03](registar-rizika.md#r-03) |
| v5.0.0-6.2.5 | Bez pravila o sastavu lozinke | ✅ | samo minimalna duljina |
| v5.0.0-6.2.6 | Polje lozinke `type=password` | ✅ | obrazac `/prijava` i `/reset` |
| v5.0.0-6.2.7 | Dopušteno lijepljenje i upravitelji lozinki | ✅ | nema blokiranja lijepljenja ni `autocomplete=off` |
| v5.0.0-6.2.8 | Lozinka se provjerava točno kako je unesena | ✅ | bez skraćivanja i promjene velikih slova; Argon2 (za razliku od bcrypta) nema ograničenje od 72 bajta |
| v5.0.0-6.3.1 | Zaštita od credential stuffinga i pogađanja | ❌ | [N-02](nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md) → [R-03](registar-rizika.md#r-03), rok 15. 12. 2026. |
| v5.0.0-6.3.2 | Nema zadanih računa (admin …) | ❌ | seed račun `admin` s poznatom lozinkom – [R-04](registar-rizika.md#r-04), blokira isporuku |
| v5.0.0-6.4.1 | Sigurne početne lozinke / aktivacijski kodovi | ➖ | aplikacija ne generira početne lozinke |
| v5.0.0-6.4.2 | Nema podsjetnika za lozinku ni „tajnih pitanja“ | ✅ | ne postoje |

### V7 Session Management

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-7.2.1 | Provjera tokena na poslužitelju | ✅ | `TokenStore` i ovisnost `Prijavljeni` (`medtermin/platforma/autentikacija.py`) |
| v5.0.0-7.2.2 | Dinamički generirani tokeni sesije | ✅ | referentni token po prijavi |
| v5.0.0-7.2.3 | Referentni token iz CSPRNG-a, ≥ 128 bita | ✅ | 256 bita: `secrets.token_urlsafe(32)` |
| v5.0.0-7.2.4 | Novi token pri prijavi, prekid trenutnog | ⚠️ | svaka prijava dobiva novi token; prethodni se ne prekida odmah, nego istječe (N-01) |
| v5.0.0-7.4.1 | Nakon odjave ili isteka sesija se ne može koristiti | ✅ | popravak [N-01](nalazi/N-01-sesija-bez-isteka.md): `tests/sigurnost/test_n01_sesija.py` |
| v5.0.0-7.4.2 | Prekid sesija kad je račun onemogućen ili obrisan | ➖ | aplikacija nema onemogućavanje ni brisanje računa |

### V8 Authorization

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-8.1.1 | Dokumentirana pravila pristupa | ✅ | [sigurnosna-pravila.md](sigurnosna-pravila.md#pristup-asvs-811) |
| v5.0.0-8.2.1 | Pristup funkcijama samo s eksplicitnim ovlastima | ✅ | uvoz samo LIJECNIK/ADMIN – `test_korisnik_ne_moze_uvoziti_termine` |
| v5.0.0-8.2.2 | Pristup zapisima samo ovlaštenima (IDOR/BOLA) | ✅ | `tests/sigurnost/test_s01_tuda_rezervacija.py`, `test_s13_fail_open.py` |
| v5.0.0-8.3.1 | Autorizacija na pouzdanom sloju | ✅ | provjere u servisima na poslužitelju |

### V9 Self-contained Tokens

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-9.1.1 | Potpis/MAC samostalnih tokena (JWT) | ➖ | referentni tokeni, ne JWT |
| v5.0.0-9.1.2 | Allowlista algoritama za samostalne tokene | ➖ | referentni tokeni, ne JWT |
| v5.0.0-9.1.3 | Ključevi za samostalne tokene iz pouzdanih izvora | ➖ | referentni tokeni, ne JWT |
| v5.0.0-9.2.1 | Provjera razdoblja valjanosti u tokenu (exp, nbf) | ➖ | referentni tokeni; istek na poslužitelju (N-01) |

### V10 OAuth and OIDC

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-10.4.1 | OAuth: redirect URI-ji iz allowliste | ➖ | aplikacija nije OAuth poslužitelj |
| v5.0.0-10.4.2 | OAuth: jednokratni autorizacijski kod | ➖ | aplikacija nije OAuth poslužitelj |
| v5.0.0-10.4.3 | OAuth: kratkotrajni autorizacijski kod | ➖ | aplikacija nije OAuth poslužitelj |
| v5.0.0-10.4.4 | OAuth: samo potrebni grantovi | ➖ | aplikacija nije OAuth poslužitelj |
| v5.0.0-10.4.5 | OAuth: zaštita od ponovne uporabe refresh tokena | ➖ | aplikacija nije OAuth poslužitelj |

### V11 Cryptography

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-11.3.1 | Bez ECB-a i slabog paddinga | ➖ | aplikacija sama ne šifrira podatke (šifriranje u bazi – Dan 2, R-09) |
| v5.0.0-11.3.2 | Samo odobreni algoritmi (AES-GCM …) | ➖ | kao 11.3.1 |
| v5.0.0-11.4.1 | Samo odobrene hash funkcije (bez MD5) | ✅ | SHA-256 za token reseta, Argon2id za lozinke (S07, S11) |

### V12 Secure Communication

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-12.1.1 | Samo TLS 1.2 i 1.3 | ⚠️ | TLS na reverse proxyju – [R-08](registar-rizika.md#r-08) |
| v5.0.0-12.2.1 | TLS za svu komunikaciju s klijentom | ⚠️ | TLS na reverse proxyju – [R-08](registar-rizika.md#r-08) |
| v5.0.0-12.2.2 | Javno pouzdani certifikati | ⚠️ | certifikat postavlja okolina – [R-08](registar-rizika.md#r-08) |

### V13 Configuration

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-13.4.1 | Bez .git i sličnih mapa u isporuci | ✅ | aplikacija ne poslužuje datoteke iz mape projekta (nema `StaticFiles`); isporučuju se samo `medtermin/` i `requirements.txt` |

### V14 Data Protection

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-14.2.1 | Osjetljivi podaci ne idu u URL | ⚠️ | token prijave samo u zaglavlju/kolačiću; jednokratni token reseta je u poveznici (`/reset?token=`), a ime datoteke nalaza u `?datoteka=` |
| v5.0.0-14.3.1 | Brisanje podataka u klijentu nakon odjave | ✅ | odjava briše kolačić `SESSION` (N-01); aplikacija ne koristi spremište preglednika |

### V15 Secure Coding and Architecture

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-15.1.1 | Dokumentirani rokovi za zakrpe ovisnosti | ✅ | [sigurnosna-pravila.md](sigurnosna-pravila.md#rokovi-za-zakrpe-ovisnosti-asvs-1511) |
| v5.0.0-15.2.1 | Komponente unutar dokumentiranih rokova | ⚠️ | vrata zelena bez ijedne iznimke (OSV-Scanner i pip-audit: 0 nalaza); Dependabot PR-ovi prolaze vrata |
| v5.0.0-15.3.1 | API vraća samo potrebna polja | ✅ | `/api/ja` bez hasha i OIB-a; rezervacije bez OIB-a |

## Odabrani L2 zahtjevi

| ASVS 5.0.0 | Zahtjev (skraćeno) | Status | Dokaz ili razlog |
|---|---|---|---|
| v5.0.0-2.3.4 | Ograničeni resurs se ne može dvaput rezervirati | ✅ | `tests/sigurnost/test_s10_zadnje_mjesto.py` (S10) |
| v5.0.0-3.4.3 | Content-Security-Policy | ⚠️ | CSP na stranici za ispis (`test_s09_ispis_xss.py`); ostale HTML stranice bez CSP-a (ZAP 10038, informativno) |
| v5.0.0-7.1.1 | Dokumentirani istek sesije | ✅ | [sigurnosna-pravila.md](sigurnosna-pravila.md#sesija) |
| v5.0.0-7.3.1 | Istek nakon neaktivnosti | ✅ | 30 min – `test_n01_sesija.py` |
| v5.0.0-7.3.2 | Najdulje trajanje sesije | ✅ | 8 h – `test_n01_sesija.py` |
| v5.0.0-7.4.3 | Prekid drugih sesija nakon promjene lozinke | ✅ | reset opoziva sve tokene – `test_n01_sesija.py` |
| v5.0.0-11.4.2 | Lozinke s KDF-om za lozinke (bcrypt, Argon2 …) | ✅ | Argon2id, `argon2-cffi` `PasswordHasher()`: t = 3, m = 64 MiB, p = 4 (RFC 9106) (S07) |
| v5.0.0-13.4.5 | Dokumentacija API-ja i nadzorni endpointi nisu izloženi bez namjere | ❌ | Swagger UI `/docs` i `/openapi.json` dostupni bez prijave (FastAPI zadano) – [R-04](registar-rizika.md#r-04) |
| v5.0.0-14.1.1 | Popis i klasifikacija osjetljivih podataka | ✅ | [uskladenost.md](uskladenost.md#1-koje-podatke-obrađujemo) |
| v5.0.0-15.1.2 | SBOM svih komponenti | ⚠️ | CycloneDX SBOM iz okruženja u svakom pokretanju (artefakt `izvjestaj-sca`); tranzitivne verzije nisu zaključane, pa isporuka može dobiti druge – [R-02](registar-rizika.md#r-02) |
| v5.0.0-16.2.5 | Osjetljivi podaci u logu prema razini zaštite | ✅ | `tests/sigurnost/test_s12_logiranje.py` (S12) |
| v5.0.0-16.3.1 | Zapis svih autentikacija, i neuspjelih | ✅ | INFO uspješna, WARNING neuspjela prijava – `test_s12_logiranje.py` |
| v5.0.0-16.4.2 | Log zaštićen od neovlaštenog pristupa i izmjene | ❌ | [R-06](registar-rizika.md#r-06) |
| v5.0.0-16.5.3 | Siguran neuspjeh, bez fail-open | ✅ | `tests/sigurnost/test_s13_fail_open.py` (S13) |

## Otvorene stavke koje nisu u registru rizika

- v5.0.0-6.2.2 / 6.2.3 – promjena lozinke iz prijavljenog računa (uz trenutnu lozinku).
- v5.0.0-3.2.1, 3.4.3 – zaglavlja `X-Content-Type-Options: nosniff`, CSP i zaštita od uokvirivanja na svim HTML
  stranicama (ZAP ih prijavljuje kao informativne).
- v5.0.0-14.2.1 – ime datoteke nalaza u URL-u (`?datoteka=nalaz-ana-krvna-slika.txt`) otkriva vrstu pretrage u
  logovima poslužitelja; bolje preuzimanje po ID-ju nalaza.
