# Vodič kroz demo – Dan 3, Python (SAMO ZA PREDAVAČA)

Demo prati prezentaciju **P3 – Ispitivanje sigurnosti, rizik i usklađenost**: za svaki blok je navedeno što otvoriti,
što reći i gdje je gotov primjer. Sve je na jednom projektu (MedTermin, **Python / FastAPI**), u stanju u kojem bi ga
polaznik predao u nedjelju. Repozitorij: <https://github.com/aradovanJava/t3-dan3-medtermin-demo-python> (privatan).
Ista priča u Javi: <https://github.com/aradovanJava/t3-dan3-medtermin-demo> – razlike su na kraju ovog vodiča.

**Ne pokazivati:** izvorni kod u `medtermin/` (referentno rješenje T2) i diff [PR #12](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/12) (to je rješenje S10).
Pokazuju se Actions, Summary vrata, PR-ovi, testovi i dokumenti u `docs/`.

## Prije nastave (10 min)

1. Otvorite u pregledniku: **Actions**, **Pull requests** (i zatvorene) i ovu mapu `docs/`.
2. Lokalno pripremite aplikaciju za blok 2 (Python 3.12+):
   `python -m venv .venv` → `source .venv/bin/activate` (Windows PowerShell: `.venv\Scripts\Activate.ps1`) →
   `pip install -r requirements-dev.txt` → `python -m medtermin`. Port 8000 mora biti slobodan.
3. Otvorite [rucni-testovi.http](rucni-testovi.http) u VS Codeu (proširenje REST Client) ili PyCharmu (HTTP Client).
4. Po želji: [dfd.png](dfd.png) u zasebnoj kartici za blok 3.

## Blok 1 · Pipeline (slajdovi 5–7)

| Korak sa slajda 6 | Što pokazati | Gdje |
|---|---|---|
| 1 Predložak u repozitorij | prvi commit: T2 projekt + mapa `python/` iz paketa (s `.github`, `.semgrepignore` i `.gitleaks.toml`) | Commits → prvi commit |
| 2 Prvo pokretanje | **zeleno bez ijedne iznimke**: SAST 0 blokirajućih (26 informativnih), SCA 0 nalaza, DAST 0 blokirajućih (14 informativnih); 43 testa (funkcionalni i primjer), pokrivenost 87 % (nakon sigurnosnih testova i N-01: 60 testova, 89 %) | [prvo pokretanje](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/actions/runs/44571696120) → Summary |
| 3 Ovisnosti | `requirements.txt` pribija 7 izravnih paketa, a pip dodaje **14 tranzitivnih bez zaključane verzije i hasha** (među njima Starlette) – vrata su zelena, ali isporuka nije ponovljiva → rizik [R-02](registar-rizika.md#r-02) | `requirements.txt`, artefakt `izvjestaj-sca` (SBOM) |
| 3 Dependabot | 9 PR-ova odmah nakon prvog pusha, **svi prolaze vrata** – i velike verzije akcija (checkout 5 → 7, download-artifact 6 → 8) i cyclonedx-bom 7 → 8. Otvoreni su prije sigurnosnih testova: zelena provjera vrijedi za stari `main` (prije spajanja `@dependabot rebase`) | Pull requests #1–#9 |
| 4 Tajne i iznimke | `ci/prihvaceno.txt` i `osv-scanner.toml` su **prazni**, a u `medtermin/` nema `# nosec` ni `# nosemgrep`: popravljeni S08 (rječnik dopuštenih stupaca) ne prijavljuje ni Semgrep ni Bandit | datoteke |
| 5 DAST s prijavom | `ci/dast-putanje.txt` – svi GET endpointi MedTermina | datoteka, artefakt `izvjestaj-dast` |
| 6 Dokaz pada | [PR #11](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/11): vraćen S06 → **Semgrep (vlastito pravilo) i SCA (OSV-Scanner + pip-audit, CVE-2020-14343, CVSS 9,8)** blokiraju ([crveno](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/actions/runs/44573163119)); [PR #12](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/12): vraćen S10 → **svi alati zeleni**, pada samo test (10 × 201 od 10 zahtjeva, [crveno](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/actions/runs/44573359360)) | PR → Checks → Summary |

**Poruka:** [PR #12](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/12) je most prema bloku 2 – propust koji nijedan alat ne vidi zaustavio je samo sigurnosni test.

U PR #11 pokažite i informativni dio Summaryja: **Bandit** je isti `yaml.load` prijavio kao B506 srednje ozbiljnosti
– ispod praga za blokiranje (`BANDIT_BLOKIRA = {"HIGH"}` u `ci/gate.py`). Blokiralo ga je vlastito Semgrep
pravilo iz `ci/semgrep/regresije.yml`, napisano baš za regresiju S06.

Pitanja za polaznike: *Zašto „zeleno bez iznimki“ još ne znači „sigurna isporuka“?* (tranzitivne ovisnosti nisu
zaključane – CI je provjerio verzije od danas) · *Zašto je PR #11 blokirao Semgrep, a ne Bandit?* (prag po alatu;
vlastito pravilo čuva poznatu regresiju) · *Zašto Dependabot PR nije automatski siguran?* (vrata ga provjeravaju
kao svaki drugi kod – i to na stanju `main` iz trenutka otvaranja PR-a).

## Blok 2 · Ispitivanje (slajdovi 8–13)

1. **Plan** – [plan-ispitivanja.md](plan-ispitivanja.md): opseg, uloge (dva korisnika!), alati, sedam ručnih testova
   s WSTG oznakama i kriterij prolaza. Ovo je primjer „plana na jednoj stranici“.
2. **Što alati ne vide** (slajd 10) – u `tests/sigurnost/` je po jedan test za S01, S09, S10, S12 i S13 (i
   S02–S04); pokreću se s `pytest -m sigurnost`. Otvorite `test_s10_zadnje_mjesto.py`: fixture `posluzitelj` iz
   `tests/sigurnost/conftest.py` pokreće **stvarni uvicorn poslužitelj** u dretvi na slobodnom portu, 10 dretvi čeka
   na `threading.Barrier`, a test traži točno jedan 201 – Python verzija isječka sa slajda 11.
   Usput: FastAPI izvršava obične (`def`) rute u skupu dretvi, a baza ima bravu po naredbi – svaka naredba je
   atomska, ali par „SELECT pa UPDATE“ nije. Utrka postoji i u jednom procesu.
3. **Ručni test uživo** (slajd 11) – [rucni-testovi.http](rucni-testovi.http) na lokalnoj aplikaciji: prijava
   ana/marko, RT-01 (DELETE tuđe rezervacije → 404), RT-05 (`format=xml` → 404, bez sadržaja).
4. **Nalaz koji je ispitivanje stvarno našlo** – RT-06: token ne istječe i nema odjave.
   [N-01](nalazi/N-01-sesija-bez-isteka.md) pokazuje sva četiri dijela zapisa nalaza sa slajda 13 (što i gdje, dokaz,
   uzrok i popravak, ponovno ispitivanje) i CVSS 4.0 vektor (8,3).
5. **Crveno → zeleno** – [PR #10](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/10): prvi commit samo test ([crveno](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/actions/runs/44573019577) – 4 od 4 testa padaju),
   drugi commit popravak ([zeleno](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/actions/runs/44573652199)). To je dokaz „test koji je bio crven, a sada je zelen“.
6. **Otvoren nalaz** – [N-02](nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md) (nema ograničenja pokušaja prijave):
   nije popravljen, ide u registar rizika s vlasnikom i rokom.

## Blok 3 · Model prijetnji (slajdovi 14–17)

- [dfd.md](dfd.md) + [dfd.png](dfd.png): 7 vanjskih entiteta, 2 procesa, 5 spremišta, 14 tokova, 3 granice
  povjerenja. Pokažite F14 (isporuka: kod + ovisnosti s PyPI-ja ulaze u poslužitelj) i D4 (sesije – tu je bio N-01).
- [stride.md](stride.md): 30 prijetnji, STRIDE po vrsti elementa; svaka ima kontrolu s dokazom (test, pravilo) ili
  ID rizika. Uključuje bazu (Dan 2), CI/CD (Dan 1: akcije po oznaci, tj-actions) i dvije prijetnje kojih u Java
  verziji nema: Swagger UI bez prijave i nezaključane tranzitivne ovisnosti.

## Blok 4 · Analiza rizika (slajdovi 18–21)

[registar-rizika.md](registar-rizika.md): 9 rizika na istim ljestvicama kao slajd 20, sva četiri postupanja
(izbjeći – R-04 seed računi i Swagger UI, smanjiti – R-03, prenijeti – R-08 TLS kod pružatelja smještaja,
prihvatiti – R-07), vlasnik i rok za svaki. R-01 je zatvoren popravkom N-01 (6 → 3). R-02 povezuje blok 1 i 4:
vrata su zelena, ali na verzijama koje je pip izabrao na dan pokretanja.

Pitanje: *Zašto R-04 (seed račun `admin`, `/docs`) ima postupanje „izbjeći“, a ne „smanjiti“?*

## Blok 5 · Usklađenost (slajdovi 22–26)

- [asvs.md](asvs.md): **svih 70 L1 zahtjeva** ASVS 5.0.0 (✅ 33 · ⚠️ 12 · ❌ 7 · ➖ 18 s razlogom) i 14 odabranih L2,
  svaki s dokazom. Pokažite da svaki ❌ vodi na rizik ili otvorenu stavku – to je razlika između liste i dokaza.
- [sigurnosna-pravila.md](sigurnosna-pravila.md): dokumentacijski ASVS zahtjevi (pristup, ulaz, sesija, rokovi za
  zakrpe, što se logira) na jednom mjestu.
- [uskladenost.md](uskladenost.md): četiri pitanja vodilje za polikliniku – posebna kategorija podataka (čl. 9),
  čl. 28 i 35, rokovi GDPR / NIS2 / CRA, pet pitanja za naručitelja.
- [SECURITY.md](../SECURITY.md): kanal za prijavu ranjivosti (CRA i ASVS traže da postoji).

## Što polaznik predaje (usporedba)

| Predaja (ZIP `Vxx-Ime-Prezime-T3.zip`) | U ovom demu |
|---|---|
| `repozitorij.txt` – repozitorij + crveno pokretanje | ovaj repozitorij + [PR #11](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/11) / [PR #12](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/12) |
| `usklađenost/` – ASVS lista, GDPR/NIS2 analiza | [asvs.md](asvs.md), [uskladenost.md](uskladenost.md) |
| `usklađenost/` – DFD sa STRIDE tablicom | [dfd.png](dfd.png), [stride.md](stride.md) |
| `usklađenost/` – registar od barem 5 rizika | [registar-rizika.md](registar-rizika.md) (9) |
| `baza/` – skripta i izlaz provjere (Dan 2) | nije dio ovog dema – vidi vodič za bazu (R-09) |

## Razlike u odnosu na Java demo

| | Java (`t3-dan3-medtermin-demo`) | Python (ovaj repozitorij) |
|---|---|---|
| Prvo pokretanje | zeleno uz 30 prihvaćenih SCA nalaza (opće iznimke za Tomcat) | zeleno bez ijedne iznimke |
| Ovisnosti (blok 1, korak 3) | PR #11: Spring Boot 3.5.16 + Tomcat 10.1.61, 7 iznimki s rokom | nema PR-a – lekcija je R-02 (tranzitivne ovisnosti bez zaključane verzije i hasha) |
| Dependabot | 10 PR-ova, 2 ne prolaze (Spring Boot 4.1, SpotBugs 4.10) | 9 PR-ova, svi prolaze |
| R-02 | platforma izvan OSS podrške (Spring Boot 3.5) | nezaključane tranzitivne ovisnosti |
| R-04 | seed računi | seed računi **i** Swagger UI `/docs` bez prijave (ASVS 13.4.5) |
| Dokaz pada S06 | snakeyaml 1.33 – SCA i Semgrep | PyYAML 5.3.1 – SCA (OSV + pip-audit) i vlastito Semgrep pravilo; Bandit samo informativno |
| SAST | Semgrep + SpotBugs/FindSecBugs | Semgrep + Bandit |
| Lozinke | bcrypt (ASVS 6.2.8 ⚠️ – ograničenje od 72 bajta) | Argon2id (6.2.8 ✅) |
| Baza u razvoju | H2 | SQLite u memoriji |
| S10 test | `@SpringBootTest(RANDOM_PORT)` + `CyclicBarrier` | uvicorn u dretvi + `threading.Barrier` |
| Pokretanje | `./mvnw spring-boot:run`, port 8080 | `python -m medtermin`, port 8000 |
| Sigurnosni testovi | `./mvnw test -Dgroups=sigurnost` | `pytest -m sigurnost` |

Brojevi nalaza, PR-ova i ASVS statusa se zato razlikuju; blokovi 2–5 (plan, nalazi N-01 i N-02, DFD, STRIDE,
registar, usklađenost) idu istim redom i s istim porukama.

## Ponovno pokretanje dema

- Novo zeleno pokretanje: Actions → *devsecops* → **Run workflow** na `main`.
- Crvena pokretanja ostaju u PR-ovima [PR #11](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/11), [PR #12](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/12) i u prvom commitu [PR #10](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/10).
- Dependabot tjedno otvara nove PR-ove – nakon nastave ih možete zatvoriti ili spojiti one koji prolaze.
- Ako posao padne zbog mreže (PyPI, preuzimanje alata), u pokretanju kliknite **Re-run failed jobs**.
- Provjera *Pregled ovisnosti u PR-u* u svakom PR-u je crvena: dependency review u privatnom repozitoriju
  traži GitHub Advanced Security. Posao ima `continue-on-error` i ne utječe na vrata – recite to prije nego što
  netko pita.
