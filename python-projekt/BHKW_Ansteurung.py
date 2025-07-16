from datetime import datetime

def anlagensteuerung_bhkw(
    Stoerung: bool,
    Schalter: bool,
    Wartungsmeldung: bool,
    Thermische_Desinfektion: bool
) -> str:
    """
    Steuert das BHKW basierend auf verschiedenen Signalen und der aktuellen Uhrzeit.

    Parameter:
    - Stoerung: True, wenn eine Störmeldung vorliegt.
    - Schalter: True, wenn der Hauptschalter eingeschaltet ist.
    - Wartungsmeldung: True, wenn eine Wartung ansteht.
    - Thermische_Desinfektion: True, wenn die thermische Desinfektion aktiv ist.

    Rückgabe:
    Ein formatiertes Status-String mit Uhrzeit.
    """

    # 1. Aktuelle Zeit ermitteln
    aktuelle_zeit = datetime.now()
    # 2. Nur die Stunde extrahieren (0–23)
    aktuelle_stunde = aktuelle_zeit.hour

    # 3. Prioritäten-Logik:
    #    a) Immer zuerst Störungen behandeln
    if Stoerung:
        status_text = "BHKW aus: Störung erkannt"
    #    b) Dann Wartungshinweise
    elif Wartungsmeldung:
        status_text = "BHKW aus: Wartung erforderlich"
    #    c) Dann thermische Desinfektion
    elif Thermische_Desinfektion:
        status_text = "BHKW aus: Thermische Desinfektion aktiv"
    #    d) Wenn der Schalter aus ist, unabhängig von der Zeit ausschalten
    elif not Schalter:
        status_text = "BHKW aus: Schalter ist ausgeschaltet"
    #    e) Innerhalb der gewünschten Betriebszeit einschalten
    elif 6 <= aktuelle_stunde < 22:
        status_text = "BHKW ein"
    #    f) Außerhalb der Betriebszeit ausschalten
    else:
        status_text = "BHKW aus: außerhalb der Betriebszeit"

    # 4. Ergebnis-String zusammenstellen und zurückgeben
    return f"{status_text} um {aktuelle_zeit.strftime('%H:%M:%S')}"

from typing import Dict, List

def berechnung_3_tage_mittelwert(
    temperaturdaten: Dict[int, List[float]]
) -> float:
    """
    Berechnet den Mittelwert der Außentemperatur über 3 Tage,
    wobei pro Tag jeweils 3 Messwerte (07:00, 14:00, 21:00) vorliegen.

    :param temperaturdaten:
        Ein Dictionary mit genau 3 Schlüsseln (1, 2, 3),
        jeweils eine Liste mit genau 3 float-Werten.
    :return:
        Der 3-Tage-Mittelwert (float).
    :raises:
        ValueError, wenn die Struktur von temperaturdaten nicht stimmt.
    """

    # 1. Eingabe validieren
    if set(temperaturdaten.keys()) != {1, 2, 3}:
        raise ValueError("temperaturdaten muss die Schlüssel 1, 2 und 3 enthalten.")
    for tag, werte in temperaturdaten.items():
        if not isinstance(werte, list) or len(werte) != 3:
            raise ValueError(f"Für Tag {tag} müssen genau 3 Messwerte übergeben werden.")

    # 2. Tagesmittelwerte berechnen
    tage_mittelwerte: List[float] = []
    for tag in sorted(temperaturdaten):
        werte = temperaturdaten[tag]
        mittelwert = sum(werte) / len(werte)
        tage_mittelwerte.append(mittelwert)
        print(f"Tagesmittelwert Tag {tag}: {mittelwert:.2f} °C")

    # 3. Gesamtmittelwert über 3 Tage
    gesamtdurchschnitt = sum(tage_mittelwerte) / len(tage_mittelwerte)
    print(f"\n🌡️ Durchschnitt der letzten 3 Tage: {gesamtdurchschnitt:.2f} °C")

    return gesamtdurchschnitt

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

from typing import Dict, List, Tuple, Optional

# Vorausgesetzte Funktionen aus deinen bisherigen Modulen:
# - anlagensteuerung_bhkw(...) -> str
# - berechnung_3_tage_mittelwert(temperaturdaten: Dict[int, List[float]]) -> float
# - berechnung_heizkennlinie(...) -> float

def steuerung_bhkw(
    status_text: str,
    temperaturdaten: Dict[int, List[float]],
    vorlauf_ist: float,
    # Parameter für die Heizkennlinien-Berechnung:
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
) -> Tuple[bool, Optional[float]]:
    """
    Regelt das BHKW nur dann auf AN, wenn:
    1) Status aus anlagensteuerung_bhkw == 'BHKW ein'
    2) 3‑Tage‑Mittelwert < 16°C
    3) vorlauf_ist < berechnung_heizkennlinie(...)
    """

    # 1) Status prüfen
    status_ein = status_text.lower().startswith("bhkw ein")

    # 2) Mittlere Außentemperatur berechnen
    mittlere_temp = berechnung_3_tage_mittelwert(temperaturdaten)

    # 3) Soll‑Vorlauftemperatur berechnen
    soll_vl = berechnung_heizkennlinie(
        messwert_außentemperatur,
        messwert_raumtemperatur,
        sollwert_raumtemperatur,
        kurve_steilheit,
        kurve_fixpunkt,
        kurve_exponent,
        min_vorlauftemp,
        max_vorlauftemp,
        nachtabsenkung_delta,
        raumtemp_komp_freigabe,
        norm_raumtemperatur,
        raumtemp_komp_prozent
    )

    # 4) Alle drei Bedingungen müssen erfüllt sein
    if status_ein and mittlere_temp < 16.0 and vorlauf_ist < soll_vl:
        print("Alle Bedingungen erfüllt → BHKW einschalten.")
        return True, soll_vl

    # Sonst ausschalten
    print("Bedingungen nicht erfüllt → BHKW ausschalten.")
    return False, None


if __name__ == "__main__":
    # Beispiel-Daten und Parameter (ersetzt durch deine Live-Werte)
    status = anlagensteuerung_bhkw(
        Stoerung=False,
        Schalter=True,
        Wartungsmeldung=False,
        Thermische_Desinfektion=False
    )

    temperaturdaten = {
        1: [12.2, 12.1, 12.4],
        2: [12.0, 12.3, 12.7],
        3: [12.8, 12.5, 12.0],
    }
    aktueller_vorlauf_ist = 30.0  # Messwert in °C

    # Heizkennlinien-Parameter
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

    # Steuerungsfunktion ausführen
    schalt_an, soll_vl = steuerung_bhkw(
        status,
        temperaturdaten,
        aktueller_vorlauf_ist,
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

    print(f"\n>>> Schaltbefehl: {'AN' if schalt_an else 'AUS'}")
    if soll_vl is not None:
        print(f">>> Soll-Vorlauftemperatur: {soll_vl:.1f} °C")
