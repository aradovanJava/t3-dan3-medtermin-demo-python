# MedTermin – kako pokrenuti

Web aplikacija privatne poliklinike za naručivanje pregleda, pregled nalaza i ispis potvrda.
Python 3.12+, FastAPI, SQLite baza u memoriji (podaci se pune pri svakom pokretanju).

## Preduvjeti

- Python 3.12 ili noviji (`python --version`; na Windowsu i `py --version`)
- VS Code (proširenja Python i Pylance) ili PyCharm: otvori mapu projekta

## Virtualno okruženje i ovisnosti

```bash
python -m venv .venv
source .venv/bin/activate            # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Pokretanje

```bash
python -m medtermin
```

ili `uvicorn medtermin.main:app --reload --port 8000`, ili u IDE-u pokreni `run.py` (u VS Codeu: *Run and Debug →
MedTermin*).

- početna stranica: http://localhost:8000/
- prijava obrascem: http://localhost:8000/prijava
- provjera rada: http://localhost:8000/api/health
- dokumentacija API-ja (Swagger UI): http://localhost:8000/docs

Primjeri zahtjeva za REST API nalaze se u `http/medtermin.http` (VS Code REST Client, PyCharm HTTP Client).

## Testovi

```bash
pytest                       # svi testovi
pytest -m funkcionalno       # funkcionalni testovi
pytest -m primjer            # primjer testa
pytest -m sigurnost          # sigurnosni testovi (propusti koje alati iz pipelinea ne vide)
pytest --cov --cov-report=html   # pokrivenost koda → htmlcov/index.html
```

Vlastite testove možeš temeljiti na fixture funkcijama iz `tests/conftest.py` (`client`, `prijava`, `novi_korisnik`,
`mape`) – pogledaj `tests/primjer/test_primjer_sigurnosnog_testa.py`. Svaki test dobiva svježu aplikaciju i bazu.

## Alati za analizu (neobavezno)

```bash
ruff check medtermin                     # stil i pravila iz Bandita (S…)
bandit -c pyproject.toml -r medtermin    # Bandit
pip-audit -r requirements.txt            # provjera ovisnosti u bazama sigurnosnih savjeta
cyclonedx-py requirements requirements.txt -o bom.json   # popis ovisnosti (SBOM)
```

`bom.json` možeš provjeriti i alatima poput OSV-Scanner ili Trivy.

## Korisnici

| Korisničko ime | Lozinka | Uloga |
|---|---|---|
| ana | `Ana12345!` | KORISNIK |
| marko | `Marko12345!` | KORISNIK |
| dr.horvat | `Ovlasteni12345!` | LIJECNIK |
| admin | `Admin12345!` | ADMIN |

API prihvaća token u zaglavlju `Authorization: Bearer <token>` (dobiva se s `POST /api/auth/login`)
ili kolačić `SESSION` koji postavlja prijava obrascem. Odjava: `POST /api/auth/odjava`.

## Konfiguracija (varijable okruženja, vidi `medtermin/postavke.py`)

| Varijabla | Značenje | Zadano |
|---|---|---|
| `APP_STORAGE_DIR` | mapa s datotekama nalaza | `./data/dokumenti` |
| `APP_MAILBOX_DIR` | mapa u koju se „šalju” e-poruke (tekstualne datoteke) | `./data/posta` |
| `APP_CORS_ALLOWED_ORIGINS` | origini frontend aplikacije (odvojeni zarezom) | `http://localhost:5173` |
| `APP_PORT` | port aplikacije | `8000` |
| `APP_SESIJA_NEAKTIVNOST_S` | istek tokena prijave nakon neaktivnosti (sekunde) | `1800` (30 min) |
| `APP_SESIJA_NAJDULJE_S` | najdulje trajanje tokena od prijave (sekunde) | `28800` (8 h) |

Poruke za promjenu lozinke ne šalju se stvarno, nego se zapisuju u `APP_MAILBOX_DIR`
(datoteka `<korisnik>-<vrijeme>.txt` s tokenom i poveznicom).
