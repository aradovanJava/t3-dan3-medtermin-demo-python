# Plan ispitivanja sigurnosti – MedTermin

> Blok 2 radionice. Plan na jednoj stranici: opseg, okolina, alati, ručni testovi i kriterij prolaza.
> Izvedeno 19. 11. 2026.; rezultati su u [nalazi/](nalazi/) i u stupcu „Rezultat“ niže.

## 1. Opseg

| | |
|---|---|
| **U opsegu** | REST API i HTML stranice MedTermina (Python 3.13, FastAPI, uvicorn), lokalna instanca `http://localhost:8000` i instanca koju pokreće CI (DAST) |
| **Izvan opsega** | infrastruktura i reverse proxy (TLS – vidi R-08), SQL Server (zasebno, laboratorij s Dana 2), ispitivanje opterećenja i DoS, socijalni inženjering |
| **Pravni okvir** | ispituje se samo vlastita lokalna ili CI instanca. Tuđi sustav nikad bez pisanog dopuštenja vlasnika. |

## 2. Okolina, uloge i podaci

- SQLite baza u memoriji, podaci se pune pri svakom pokretanju (`medtermin/pocetni_podaci.py`); nikakvi stvarni
  podaci.
- Uloge: anonimni korisnik · `KORISNIK` (**dva** korisnika – `ana`, `marko` – nužna za kontrolu pristupa) ·
  `LIJECNIK` (`dr.horvat`) · `ADMIN` (`admin`). Lozinke su u `KAKO-POKRENUTI.md`.
- Testni OIB-i iz seeda (`48291736504` …), testni korisnici iz testova (`utrka…`, `sesija…`).

## 3. Standardi

- **OWASP WSTG v4.2** – oznake testova (zadnja stabilna verzija).
- **OWASP ASVS 5.0.0** – razina L1 (svi zahtjevi koji se odnose na aplikaciju) i odabrani L2 – [asvs.md](asvs.md).

## 4. Automatski alati (sigurnosna vrata u pipelineu)

| Alat | Što pokriva | Gdje je rezultat |
|---|---|---|
| Semgrep (+ vlastita pravila `ci/semgrep/regresije.yml`) | obrasci u kodu (SQLi, XXE, YAML, …) | Actions → Summary, artefakt `izvjestaj-sast` |
| Bandit | obrasci u Python kodu (blokira od visoke ozbiljnosti) | isto |
| CycloneDX SBOM + OSV-Scanner + pip-audit | poznate ranjivosti ovisnosti (i tranzitivnih koje je CI instalirao) | artefakt `izvjestaj-sca` |
| gitleaks | tajne u cijeloj povijesti | artefakt `izvjestaj-tajne` |
| OWASP ZAP baseline (s prijavom) | pasivno: zaglavlja, kolačići, CSP, CORS | artefakt `izvjestaj-dast` |
| pytest – funkcionalni i **sigurnosni testovi** (`-m sigurnost`) | logika koju alati ne vide | artefakt `izvjestaj-build` |

## 5. Ručni testovi (ono što alati ne vide)

Zahtjevi su u [rucni-testovi.http](rucni-testovi.http). Svaki ručni test mora imati i automatski test – to je
jedina zaštita od regresije. Testovi su u `tests/sigurnost/`.

| ID | WSTG v4.2 | Što | Očekivano | Automatski test | Rezultat |
|---|---|---|---|---|---|
| RT-01 | ATHZ-04 | ana briše markovu rezervaciju (S01) | 403/404, zapis ostaje | `test_s01_tuda_rezervacija.py` | ✅ prolazi |
| RT-02 | INPV-02 | `<script>` u napomeni, otvoriti ispis (S09) | kodirano, CSP | `test_s09_ispis_xss.py` | ✅ prolazi |
| RT-03 | BUSL-05 | 10 istodobnih rezervacija zadnjeg mjesta (S10) | točno 1 × 201 | `test_s10_zadnje_mjesto.py` | ✅ prolazi |
| RT-04 | – (ASVS 16.2.5, 16.3.1) | log nakon prijave, rezervacije i neuspjele prijave (S12) | nema lozinke ni punog OIB-a; WARNING | `test_s12_logiranje.py` | ✅ prolazi |
| RT-05 | ERRH-01, ATHZ-02 | marko traži anin nalaz s `format=xml` (S13) | 4xx, bez sadržaja i tracebacka | `test_s13_fail_open.py` | ✅ prolazi |
| RT-06 | SESS-06, SESS-07 | token nakon odjave, nakon neaktivnosti, nakon promjene lozinke | 401 | `test_n01_sesija.py` | ❌ → ✅ **nalaz N-01**, popravljen |
| RT-07 | ATHN-03 | 20 pogrešnih prijava za `marko`, zatim ispravna | blokada ili odgoda nakon nekoliko pokušaja | – | ❌ **nalaz N-02**, otvoren (R-03) |

## 6. Kriterij prolaza

1. Sigurnosna vrata zelena na `main` (nijedan blokirajući nalaz; svaka iznimka uska i s obrazloženjem).
2. Svi testovi prolaze – funkcionalni i sigurnosni.
3. Dokaz da vrata padaju kad se propust vrati (grane `dokaz/regresija-*`, vidi [README.md](README.md)).
4. Svaki nalaz zapisan ([nalazi/](nalazi/)); visoki rizik bez odluke vlasnika blokira isporuku.

## 7. Izvještaj

Nalazi: [N-01 – sesija bez isteka](nalazi/N-01-sesija-bez-isteka.md) (popravljen),
[N-02 – nema zaštite od pogađanja lozinke](nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md) (otvoren, R-03).
Nakon popravka svaki se nalaz ponovno ispituje istim koracima.
