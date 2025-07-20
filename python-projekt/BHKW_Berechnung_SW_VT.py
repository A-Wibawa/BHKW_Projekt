import numpy as np
import matplotlib.pyplot as plt
from typing import Optional
from datetime import datetime

# Heizkennlinien-Funktion mit optionaler Stundenzuordnung
def berechnung_heizkennlinie(
    messwert_außentemperatur: float,
    messwert_raumtemperatur: float,
    sollwert_raumtemperatur: float,
    kurve_steilheit: float,
    kurve_fixpunkt: float,
    kurve_exponent: float,
    min_vorlauftemp: float,
    max_vorlauftemp: Optional[float],
    nachtabsenkung_delta: float,
    raumtemp_komp_freigabe: bool,
    norm_raumtemperatur: float,
    raumtemp_komp_prozent: float,
    current_hour: Optional[int] = None
) -> float:
    """
    Berechnet die Soll-Vorlauftemperatur anhand der Heizkennlinie,
    mit Nachtabsenkung und optionaler Raumkompensation.
    """
    # Stunde bestimmen
    stunde = current_hour if current_hour is not None else datetime.now().hour
    # Nachtabsenkung
    ist_nacht = (stunde >= 22) or (stunde < 6)
    # Basis-Kennlinie
    basis = (
        kurve_steilheit
        * (norm_raumtemperatur - messwert_außentemperatur) ** kurve_exponent
        + kurve_fixpunkt
    )
    if ist_nacht:
        basis -= nachtabsenkung_delta
    # Raumkompensation
    if raumtemp_komp_freigabe:
        diff = sollwert_raumtemperatur - messwert_raumtemperatur
        basis += diff * (raumtemp_komp_prozent / 100)
    # Begrenzung
    temp_vl = max(basis, min_vorlauftemp)
    if max_vorlauftemp is not None:
        temp_vl = min(temp_vl, max_vorlauftemp)
    return temp_vl

# Funktion zur Visualisierung der reinen Heizkennlinie
def plot_heizkennlinie(
    kurve_steilheit: float,
    kurve_fixpunkt: float,
    kurve_exponent: float,
    min_vorlauftemp: float,
    max_vorlauftemp: Optional[float],
    norm_raumtemperatur: float
) -> None:
    ta_range = np.linspace(-10, 10, 100)
    vl_range = (
        kurve_steilheit
        * (norm_raumtemperatur - ta_range) ** kurve_exponent
        + kurve_fixpunkt
    )
    vl_clipped = np.maximum(vl_range, min_vorlauftemp)
    if max_vorlauftemp is not None:
        vl_clipped = np.minimum(vl_clipped, max_vorlauftemp)
    plt.figure(figsize=(6, 4))
    plt.plot(ta_range, vl_clipped, label="Heizkennlinie")
    plt.xlabel("Außentemperatur (°C)")
    plt.ylabel("Vorlauftemperatur (°C)")
    plt.title("Heizkennlinie")
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # Statische Kennlinien-Parameter
    Raumtemp_aktuell = 21.0
    Raumtemp_soll = 22.0
    K_steil = 1.5
    K_fix = 25.0
    K_exp = 1.2
    MIN_VL = 15.0
    MAX_VL = 85.0
    NACHT_DELTA = 5.0
    RT_KOMP_FG = False
    NORM_RT = 20.0
    RT_KOMP_P = 10.0

    # 1. Simulation: Benutzerdefinierte Außentemperatur pro Stunde (1–24)
    Außentemp = [
        1, 1, 2, 4, 5, 6, 8, 10, 12, 14, 15, 16,
        17, 16, 15, 14, 12, 10, 8, 6, 4, 3, 2, 1
    ]
    hours = list(range(1, len(outside_temps) + 1))

    # 2. Vorlauftemperaturen simulieren
    vl_temps = [
        berechnung_heizkennlinie(
            ta,
            Raumtemp_aktuell,
            Raumtemp_soll,
            K_steil,
            K_fix,
            K_exp,
            MIN_VL,
            MAX_VL,
            NACHT_DELTA,
            RT_KOMP_FG,
            NORM_RT,
            RT_KOMP_P,
            current_hour=(hour-1)
        )
        for hour, ta in zip(hours, outside_temps)
    ]

    # 3. Ausgabe der Simulation
    for hour, (ta, tvl) in enumerate(zip(Außentemp, vl_temps), start=1):
        print(f"{hour:02d}:00 - Außentemp: {ta:2.0f} °C → Vorlauftemp: {tvl:.2f} °C")

    # 4. Plot: Simulation
    plt.figure(figsize=(10, 5))
    plt.plot(hours, Außentemp, marker='o', label="Außentemperatur")
    plt.plot(hours, vl_temps, marker='s', label="Soll-Vorlauftemperatur")
    plt.title("Vorlauftemperatur über 24h bei stündlich variierender Außentemperatur")
    plt.xlabel("Stunde des Tages (1–24)")
    plt.ylabel("Temperatur (°C)")
    plt.xticks(hours)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 5. Plot: reine Heizkennlinie
    plot_heizkennlinie(
        kurve_steilheit=K_steil,
        kurve_fixpunkt=K_fix,
        kurve_exponent=K_exp,
        min_vorlauftemp=MIN_VL,
        max_vorlauftemp=MAX_VL,
        norm_raumtemperatur=NORM_RT
    )
