"""Pokretanje: ``python -m medtermin`` (http://localhost:8000)."""

import uvicorn

from medtermin.postavke import Postavke


def main() -> None:
    uvicorn.run("medtermin.main:app", host="127.0.0.1", port=Postavke().port)


if __name__ == "__main__":
    main()
