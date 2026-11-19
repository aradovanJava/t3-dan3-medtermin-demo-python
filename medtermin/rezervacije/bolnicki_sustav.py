"""Klijent bolničkog informacijskog sustava (BIS) koji upisuje pacijenta u raspored ordinacije.

U lokalnom okruženju BIS nije dostupan pa klijent nakon uobičajenog vremena odziva vraća lokalno
generiranu oznaku upisa.
"""

from __future__ import annotations

import itertools
import threading
import time

VRIJEME_ODZIVA = 0.15  # sekunde


class BolnickiSustavKlijent:
    def __init__(self) -> None:
        self._brojac = itertools.count(1001)
        self._brava = threading.Lock()

    def upisi_u_raspored(self, termin_id: int, pacijent: str) -> str:
        time.sleep(VRIJEME_ODZIVA)
        with self._brava:
            broj = next(self._brojac)
        return f"BIS-{termin_id}-{broj}"
