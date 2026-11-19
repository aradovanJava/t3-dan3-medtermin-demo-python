# Analiza usklađenosti – MedTermin (GDPR, NIS2 / ZKS, CRA)

> Blok 5 radionice: odgovori na četiri pitanja vodilje za domenu MedTermin (privatna poliklinika).
> **Ovo nije pravna procjena** – cilj je da razvojni tim zna koja pitanja postaviti naručitelju i kako ona mijenjaju
> zahtjeve za kod. Opseg NIS2 i CRA ovisi o činjenicama koje u projektu ne znamo (veličina, djelatnost,
> kategorizacija, način prodaje). Stanje: 19. 11. 2026.

## 1. Koje podatke obrađujemo?

Popis prema DFD-u ([dfd.md](dfd.md)) – svako spremište i tok (ASVS v5.0.0-14.1.1):

| Gdje | Podaci | Kategorija | Zaštita danas | Rok čuvanja |
|---|---|---|---|---|
| D1 `korisnici` | ime, prezime, e-pošta, OIB, hash lozinke (Argon2id), uloga | osobni podaci; OIB osobni identifikator | API ne vraća hash ni OIB; u produkciji šifriranje OIB-a (Dan 2) – R-09 | dok postoji račun – **pitanje za naručitelja** |
| D1 `rezervacije` | pacijent, termin, napomena (slobodan tekst – često simptomi), OIB | **zdravstveni podaci – posebna kategorija (GDPR čl. 9)** | pristup samo vlasniku i administratoru (S01, `test_s01_tuda_rezervacija.py`) | prema propisima o medicinskoj dokumentaciji – **potvrđuje naručitelj** |
| D1 `nalazi` + D2 datoteke | naziv i sadržaj nalaza | **posebna kategorija (čl. 9)** | samo vlasnik i administrator (S02, S13); u produkciji TDE i šifrirane kopije (Dan 2) | kao gore |
| D1 `reset_tokeni` | korisničko ime, hash tokena, vrijeme isteka | tehnički / osobni | jednokratan, 15 minuta, u bazi samo hash | brisati nakon isteka – otvorena stavka |
| D3 log | korisničko ime, maskirani OIB, vrijeme i radnja | osobni podaci | bez lozinke i punog OIB-a (`test_s12_logiranje.py`) | **pitanje za naručitelja** (npr. 12 mjeseci) – R-06 |
| D4 sesije | token → korisnik | tehnički | istek 30 min / 8 h, odjava (N-01) | do isteka |
| F9 e-pošta | poveznica s tokenom za reset | osobni | jednokratan token | – |
| F10 BIS | termin i korisničko ime pacijenta | zdravstveni kontekst | **pitanje:** koji su podaci stvarno nužni (minimizacija, čl. 5(1)(c)) | – |

**Posljedica za kod:** zdravstveni podaci podižu utjecaj u registru rizika na 3 i traže zapis pristupa nalazima
(tko je čitao), šifriranje u bazi i minimizaciju podataka prema BIS-u. Opsežna obrada posebnih kategorija
vjerojatno traži **procjenu učinka na zaštitu podataka** (GDPR čl. 35) prije puštanja u rad.

## 2. Tko je odgovoran?

| Uloga | Tko | Napomena |
|---|---|---|
| Voditelj obrade | poliklinika (naručitelj) | određuje svrhu i sredstva obrade |
| Izvršitelj obrade | razvojni tim / održavatelj aplikacije | ako aplikaciju razvijamo **i održavamo** za polikliniku – potreban je **ugovor iz čl. 28** |
| Vlasnik rizika | voditelj IT-a poliklinike (poslovni rizici), voditelj razvoja (CI/CD, platforma) | prihvaća preostali rizik – [registar](registar-rizika.md) |
| Službenik za zaštitu podataka | poliklinika | obrada posebnih kategorija u velikom opsegu – vjerojatno obvezan (čl. 37) |
| Kontakt za incidente | poliklinika + dežurni u razvojnom timu | tko koga zove u prvih 24 sata |
| Prijava ranjivosti | [SECURITY.md](../SECURITY.md) | kanal za istraživače i korisnike |

**Prvo pitanje za naručitelja:** tko je voditelj, a tko izvršitelj obrade – i tko vodi evidenciju obrade.

## 3. Kako dokazujemo kontrole?

- **ASVS 5.0.0** – svi L1 i odabrani L2 zahtjevi, svaki s dokazom: [asvs.md](asvs.md).
- **Sigurnosna vrata** na svakom pushu i PR-u (SAST, SCA + SBOM, tajne, DAST, testovi) – Actions → Summary;
  dokaz da vrata padaju: PR-ovi `DOKAZ – ne spajati` ([PR #11](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/11), [PR #12](https://github.com/aradovanJava/t3-dan3-medtermin-demo-python/pull/12)).
- **Sigurnosni testovi** za propuste koje alati ne vide: `tests/sigurnost/` (`pytest -m sigurnost`).
- **Model prijetnji i rizici**: [dfd.md](dfd.md), [stride.md](stride.md), [registar-rizika.md](registar-rizika.md).
- **Dokumentirana pravila** (pristup, ulaz, sesija, zakrpe, log): [sigurnosna-pravila.md](sigurnosna-pravila.md).
- **Baza** (SQL Server, Dan 2): skripta i izlaz automatske provjere – preduvjet isporuke (R-09).

Što **nije** dokaz: „implementirano“, snimka zaslona bez datuma i commita, poveznica na dokumentaciju okvira.

## 4. Što kad pođe po zlu?

| Propis | Kada | Rok | Kome |
|---|---|---|---|
| GDPR čl. 33 | povreda osobnih podataka (npr. procurjeli nalazi) | bez nepotrebnog odgađanja, gdje je izvedivo **72 sata** od saznanja | nadzorno tijelo – u Hrvatskoj **AZOP** |
| GDPR čl. 34 | povreda s visokim rizikom za ispitanike (zdravstveni podaci – vjerojatno) | bez nepotrebnog odgađanja | pacijentima |
| NIS2 / Zakon o kibernetičkoj sigurnosti (NN 14/2024) | značajni incident – **ako je poliklinika subjekt u opsegu** (zdravstvo je sektor visoke kritičnosti; ovisi o veličini i kategorizaciji) | rano upozorenje **24 h**, obavijest **72 h**, završno izvješće **1 mjesec** | nadležni CSIRT / tijelo |
| CRA (Uredba (EU) 2024/2847) | **samo ako se MedTermin prodaje kao proizvod s digitalnim elementima** (ne kao usluga za jednu polikliniku); od 11. 9. 2026. prijava aktivno iskorištenih ranjivosti | **24 h** / **72 h** / **14 dana** nakon korektivne mjere | ENISA i nadležni CSIRT |

**Za tim:** u izvršiteljskom ugovoru (čl. 28) treba stajati koliko brzo izvršitelj obavještava voditelja o
povredi – voditelj mora stići prijaviti u 72 sata. Zapis pristupa nalazima (R-06) odgovara na prvo pitanje
nadzornog tijela: *čiji su podaci pogođeni?*

## Otvorena pitanja za naručitelja

1. Tko je voditelj, a tko izvršitelj obrade; tko je službenik za zaštitu podataka?
2. Koliko dugo čuvamo rezervacije, nalaze, log i neaktivne račune?
3. Je li poliklinika subjekt u opsegu Zakona o kibernetičkoj sigurnosti (kategorizacija)?
4. Koji su podaci nužni bolničkom informacijskom sustavu (BIS)?
5. Planira li se MedTermin prodavati drugim poliklinikama kao proizvod (CRA)?
