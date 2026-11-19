# N-02 · Broj pokušaja prijave nije ograničen

| | |
|---|---|
| **Status** | ⏳ otvoren – rizik [R-03](../registar-rizika.md#r-03), rok 15. 12. 2026. |
| **Pronađeno** | ručnim ispitivanjem, RT-07 u [planu ispitivanja](../plan-ispitivanja.md) |
| **Mjesto** | `POST /api/auth/login` i `POST /prijava` (`KorisnikService.prijava` u `medtermin/platforma/korisnici.py`) |
| **CWE** | CWE-307 Improper Restriction of Excessive Authentication Attempts |
| **WSTG v4.2** | WSTG-ATHN-03 (slab mehanizam zaključavanja) |
| **ASVS 5.0.0** | v5.0.0-6.3.1 (L1) · v5.0.0-6.1.1 (L1, dokumentacija) · v5.0.0-6.2.4 (L1, česte lozinke) |
| **CVSS 4.0** | `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N` → **8,3 (visoka)** |

## 1. Što i gdje

Prijava prihvaća neograničen broj pokušaja za isti račun i s iste adrese. Registracija je otvorena, a lozinka mora
imati samo 8 znakova (bez provjere prema popisu čestih lozinki). Pogađanje lozinke ili credential stuffing
(lozinke iz tuđih curenja) zato je izvedivo alatom. Argon2 usporava svaki pokušaj na poslužitelju, ali ne
ograničava njihov broj – a cijenu memorije plaća poslužitelj (R-07).

**Obrazloženje CVSS-a:** AT:P jer uspjeh ovisi o tome ima li žrtva slabu ili ponovno korištenu lozinku; ostalo kao
kod N-01.

## 2. Dokaz

1. 20 × `POST /api/auth/login` `{"username": "marko", "password": "pogresna"}` → svaki put `401`, bez odgode.
2. `POST /api/auth/login` s ispravnom lozinkom → `200`.

U logu je 20 redaka `WARNING … Neuspjela prijava za korisnika marko` – zapis postoji (ASVS 16.3.1), ali nitko na
njega ne reagira.

## 3. Prijedlog popravka

- nakon 5 neuspjelih pokušaja u 15 minuta za isti račun **ili** istu IP adresu: odgoda i odgovor `429`
  (ne trajno zaključavanje – njime bi napadač mogao zaključati tuđi račun);
- provjera nove lozinke prema popisu najčešćih lozinki (ASVS 6.2.4);
- pravila zapisati u [sigurnosna-pravila.md](../sigurnosna-pravila.md#prijava) (ASVS 6.1.1);
- sigurnosni test: 6. pokušaj vraća `429`, a ispravna prijava nakon isteka odgode radi.

## 4. Privremena odluka

Dok popravak nije isporučen: neuspjele prijave zapisuju se kao `WARNING` (dokaz: `test_s12_logiranje.py`) i prate
se. Vlasnik rizika: voditelj IT-a poliklinike. Ponovno ispitivanje nakon popravka – istim koracima.
