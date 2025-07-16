import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Union

def berechnung_heizkennlinie(
    messwert_außentemperatur: float,
    messwert_raumtemperatur: float,
    sollwert_raumtemperatur: float,
    kurve_steilheit: float,
    kurve_fixpunkt: float,
    kurve_exponent: float,
    min_vorlauftemp: float,
    max_vorlauftemp: float,
    nachtabsenkung_delta: float,
    raumtemp_komp_freigabe: bool,
    norm_raumtemperatur: float,
    raumtemp_komp_prozent: float
) -> float:
    """
    Berechnet die Soll-Vorlauftemperatur anhand einer Heizkennlinie
    und zusätzlicher Raumtemperaturkompensation sowie Nachtabsenkung.

    Rückgabe:
        Soll-Vorlauftemperatur in °C (auf min/max begrenzt)
    """

    # 1. Aktuelle Stunde ermitteln
    jetzt = datetime.now()
    stunde = jetzt.hour

    # 2. Nachtabsenkung aktiv von 22:00 bis 06:00?
    ist_nacht = (stunde >= 22) or (stunde < 6)

    # 3. Basis: Heizkurve
    #    Formel: K * (T_norm - T_außen)**exponent + B
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

    # 6. Begrenzung auf min/max
    soll_vorlauftemp = max(min_vorlauftemp, min(max_vorlauftemp, basis_vorlauf))

    return soll_vorlauftemp


def plot_heizkurve(
    kurve_steilheit: float,
    kurve_fixpunkt: float,
    kurve_exponent: float,
    min_vorlauftemp: float,
    max_vorlauftemp: float,
    norm_raumtemperatur: float
) -> None:
    """
    Plottet die Heizkennlinie (ohne Nachtabsenkung und Raumkompensation)
    über einen Außentemperatur-Bereich von -10 bis +20 °C.
    """

    # Außentemperaturen von -10 bis +20 °C
    ta_range = np.linspace(-10, 20, 100)

    # Heizkurve berechnen
    vl_range = (
        kurve_steilheit
        * (norm_raumtemperatur - ta_range) ** kurve_exponent
        + kurve_fixpunkt
    )

    # Auf minimale/maximale Vorlauftemperatur beschneiden
    vl_clipped = np.clip(vl_range, min_vorlauftemp, max_vorlauftemp)

    # Plot erstellen
    plt.plot(ta_range, vl_clipped, label="Heizkennlinie")
    plt.xlabel("Außentemperatur (°C)")
    plt.ylabel("Vorlauftemperatur (°C)")
    plt.title("Heizkennlinie ohne Zusatzkompensation")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # Beispiel-Parameter
    Außentemp = 5.0
    Raumtemp_aktuell = 21.0
    Raumtemp_soll = 22.0

    K_steil = 1.5
    K_fix = 25.0
    K_exp = 1.2

    MIN_VL = 15.0
    MAX_VL = 55.0
    NACHT_DELTA = 5.0

    RT_KOMP_FG = False
    NORM_RT = 20.0
    RT_KOMP_P = 10.0

    # Sollwert berechnen und ausgeben
    soll_vl = berechnung_heizkennlinie(
        Außentemp,
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
        RT_KOMP_P
    )
    print(f"Berechnete Soll-Vorlauftemperatur: {soll_vl:.1f} °C")

    # Heizkurve visualisieren
    plot_heizkurve(K_steil, K_fix, K_exp, MIN_VL, MAX_VL, NORM_RT)