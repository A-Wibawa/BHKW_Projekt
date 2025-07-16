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
    Regelt das BHKW anhand:
    1) Status-Text der Anlagensteuerung (OK = 'ein')
    2) Mittlere Außentemperatur der letzten 3 Tage (<16°C)
    3) Ist-Vorlauftemperatur vs. Soll-Vorlauftemperatur

    Rückgabe:
        (schalt_an: bool, soll_vorlauftemp: float oder None)
    """

    # 1. Wenn der erste Status bereits auf 'ein' steht -> AN
    if status_text.lower().startswith("bhkw ein"):
        print("Status ‚ein‘ erkannt → BHKW wird eingeschaltet.")
        return True, None

    # 2. Mittlere Außentemperatur der letzten 3 Tage auswerten
    mittlere_temp = berechnung_3_tage_mittelwert(temperaturdaten)
    if mittlere_temp < 16.0:
        # Tiefere Außentemperatur → BHKW einschalten mit berechnetem Sollwert
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
        print(f"Mittlere Außentemp {mittlere_temp:.1f}°C < 16°C → BHKW einschalten.")
        return True, soll_vl

    # 3. Prüfen, ob Ist-Vorlauftemp unter dem Sollwert liegt
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
    if vorlauf_ist < soll_vl:
        print(f"Ist-Vorlauftemp {vorlauf_ist:.1f}°C < Soll {soll_vl:.1f}°C → BHKW einschalten.")
        return True, soll_vl

    # 4. Keine Bedingung erfüllt → AN-Aus
    print("Keine Regelbedingung erfüllt → BHKW ausschalten.")
    return False, soll_vl


if __name__ == "__main__":
    # Beispiel-Daten und Parameter (ersetzt durch deine Live-Werte)
    status = anlagensteuerung_bhkw(
        Stoerung=False,
        Schalter=True,
        Wartungsmeldung=False,
        Thermische_Desinfektion=False
    )

    temperaturdaten = {
        1: [15.2, 20.1, 17.4],
        2: [16.0, 21.3, 18.7],
        3: [14.8, 19.5, 17.0],
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
