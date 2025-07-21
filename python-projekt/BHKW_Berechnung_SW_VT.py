
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
    Berechnet die Soll-Vorlauftemperatur anhand einer Heizkennlinie
    und zusätzlicher Raumtemperaturkompensation sowie Nachtabsenkung.

    Rückgabe:
        Soll-Vorlauftemperatur in °C (auf min begrenzt, max optional begrenzt)
    """

    # 1. Aktuelle Stunde ermitteln
    jetzt = datetime.now()
    stunde = jetzt.hour

    # 2. Nachtabsenkung aktiv von 22:00 bis 06:00?
    ist_nacht = (stunde >= 22) or (stunde < 6)

    # 3. Basis: Heizkurve (K * (T_norm - T_außen)**exponent + B)
    basis_vorlauf = (
        kurve_steilheit
        * (norm_raumtemperatur - messwert_außentemperatur) ** kurve_exponent
        + kurve_fixpunkt
    )

    # 4. Nachtabsenkung abziehen (falls aktiv)
    if ist_nacht:
        basis_vorlauf -= nachtabsenkung_delta

    # 5. Raumtemperaturkompensation (nur bei Freigabe)
    if raumtemp_komp_freigabe:
        diff_raummess = sollwert_raumtemperatur - messwert_raumtemperatur
        kompensation = diff_raummess * (raumtemp_komp_prozent / 100)
        basis_vorlauf += kompensation

    # 6. Begrenzung auf min und optional auf max
    soll_vorlauftemp = basis_vorlauf
    if soll_vorlauftemp < min_vorlauftemp:
        soll_vorlauftemp = min_vorlauftemp
    if max_vorlauftemp is not None and soll_vorlauftemp > max_vorlauftemp:
        soll_vorlauftemp = max_vorlauftemp

    return soll_vorlauftemp

# Funktion zur Visualisierung der reinen Heizkennlinie
def plot_heizkennlinie(
    kurve_steilheit: float,
    kurve_fixpunkt: float,
    kurve_exponent: float,
    min_vorlauftemp: float,
    max_vorlauftemp: Optional[float],
    norm_raumtemperatur: float
) -> None:
    """
    Plottet die Heizkennlinie (ohne Nachtabsenkung und Raumkompensation)
    über einen Außentemperatur-Bereich von -10 bis +20 °C.

    max_vorlauftemp optional: bei None kein oberes Limit.
    """

    # Außentemperaturen von -10 bis +20 °C
    ta_range = np.linspace(-10, 20, 100)

    # Heizkurve berechnen
    vl_range = (
        kurve_steilheit
        * (norm_raumtemperatur - ta_range) ** kurve_exponent
        + kurve_fixpunkt
    )

    # Auf minimale Vorlauftemperatur beschneiden
    vl_clipped = np.maximum(vl_range, min_vorlauftemp)
    # Oberes Limit nur, wenn angegeben
    if max_vorlauftemp is not None:
        vl_clipped = np.minimum(vl_clipped, max_vorlauftemp)

    # Plot erstellen
    plt.plot(ta_range, vl_clipped, label="Heizkennlinie")
    plt.xlabel("Außentemperatur (°C)")
    plt.ylabel("Vorlauftemperatur (°C)")
    plt.title("Heizkennlinie ohne Zusatzkompensation")
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
    hours = list(range(1, len(Außentemp) + 1))

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
        for hour, ta in zip(hours, Außentemp)
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
