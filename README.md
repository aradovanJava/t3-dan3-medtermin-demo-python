# MedTermin (Python) – demo za Tjedan 3, Dan 3 (SAMO ZA PREDAVAČA)

Privatni demo repozitorij Secure Coding akademije: T2 projekt **MedTermin (Python, FastAPI)** s DevSecOps
predloškom iz T3 paketa, na kojem je uživo prikazano svih pet blokova radionice *Ispitivanje sigurnosti, rizik i
usklađenost* (P3). Java verzija iste priče: [t3-dan3-medtermin-demo](https://github.com/aradovanJava/t3-dan3-medtermin-demo).

> Aplikacija je **referentno rješenje T2** (svih 13 propusta popravljeno). Na nastavi ne otvarajte izvorni kod u
> `medtermin/` niti diff grane `dokaz/regresija-s10` – pokazujte Actions, Summary, PR-ove, testove i `docs/`.

**Vodič kroz demo po blokovima: [docs/README.md](docs/README.md)**

| Blok | Gdje |
|---|---|
| 1 · Pipeline | Actions → *devsecops*; PR-ovi „DOKAZ – ne spajati“ i Dependabot, `requirements.txt` (R-02) |
| 2 · Ispitivanje | [docs/plan-ispitivanja.md](docs/plan-ispitivanja.md), [docs/rucni-testovi.http](docs/rucni-testovi.http), [docs/nalazi/](docs/nalazi/), `tests/sigurnost/` |
| 3 · Model prijetnji | [docs/dfd.md](docs/dfd.md), [docs/stride.md](docs/stride.md) |
| 4 · Analiza rizika | [docs/registar-rizika.md](docs/registar-rizika.md) |
| 5 · Usklađenost | [docs/asvs.md](docs/asvs.md), [docs/uskladenost.md](docs/uskladenost.md), [docs/sigurnosna-pravila.md](docs/sigurnosna-pravila.md), [SECURITY.md](SECURITY.md) |

Pokretanje aplikacije i testova: [KAKO-POKRENUTI.md](KAKO-POKRENUTI.md) (`python -m medtermin`,
`pytest -m sigurnost`).
