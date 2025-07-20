from datetime import datetime
from typing import Dict, List

def anlagensteuerung_bhkw(
    Stoerung: bool,
    Schalter: bool,
    Wartungsmeldung: bool,
    Thermische_Desinfektion: bool
) -> str:
    """
    Steuert das BHKW basierend auf Signalen und Uhrzeit.
    Gibt einen Status-String zurück, z.B. "BHKW ein um 14:23:05" oder
    "BHKW aus: <Grund> um HH:MM:SS".
    """
    aktuelle_zeit = datetime.now()
    h = aktuelle_zeit.hour

    if Stoerung:
        status = "BHKW aus: Störung erkannt"
    elif Wartungsmeldung:
        status = "BHKW aus: Wartung erforderlich"
    elif Thermische_Desinfektion:
        status = "BHKW aus: Thermische Desinfektion aktiv"
    elif not Schalter:
        status = "BHKW aus: Schalter ist ausgeschaltet"
    elif 6 <= h < 22:
        status = "BHKW ein"
    else:
        status = "BHKW aus: außerhalb der Betriebszeit"

    return f"{status} um {aktuelle_zeit.strftime('%H:%M:%S')}"

def berechnung_3_tage_mittelwert(
    temperaturdaten: Dict[int, List[float]]
) -> float:
    """
    Berechnet den Durchschnitt der Außentemperatur über 3 Tage.
    Erwartet temperaturdaten = {1: [t1,t2,t3], 2: [...], 3: [...]}.
    """
    if set(temperaturdaten.keys()) != {1, 2, 3}:
        raise ValueError("Temperaturdaten muss die Schlüssel 1, 2 und 3 enthalten.")
    for tag, werte in temperaturdaten.items():
        if not isinstance(werte, list) or len(werte) != 3:
            raise ValueError(f"Für Tag {tag} müssen genau 3 Messwerte vorliegen.")

    tage_mw = [sum(temperaturdaten[tag]) / 3 for tag in sorted(temperaturdaten)]
    return sum(tage_mw) / 3

def ansteuerung_bhkw(
    Stoerung: bool,
    Schalter: bool,
    Wartungsmeldung: bool,
    Thermische_Desinfektion: bool,
    temperaturdaten: Dict[int, List[float]]
) -> str:
    """
    Gibt den Schaltbefehl 'AN' oder 'AUS' zurück:
      - 'AN', wenn das BHKW laut anlagensteuerung_bhkw ein ist
         UND der 3‑Tage‑Mittelwert ≤ 18°C.
      - 'AUS' sonst (wenn BHKW aus oder Mittelwert > 18°C).
    """
    status = anlagensteuerung_bhkw(
        Stoerung, Schalter, Wartungsmeldung, Thermische_Desinfektion
    )
    # prüfen, ob Code1 "ein" meldet
    is_on = status.startswith("BHKW ein")

    avg_temp = berechnung_3_tage_mittelwert(temperaturdaten)

    if is_on and avg_temp <= 18.0:
        return "AN"
    else:
        return "AUS"


if __name__ == "__main__":
    # Beispiel-Flags
    Stoerung = False
    Schalter = True
    Wartungsmeldung = False
    Thermische_Desinfektion = False

    # Beispiel-Temperaturdaten (3 Tage × 3 Messwerte)
    beispiel_daten = {
        1: [33.2, 30.1, 33.4],
        2: [33.0, 33.3, 33.7],
        3: [33.8, 33.5, 33.0],
    }

    # Schaltbefehl ermitteln und ausgeben
    schaltbefehl = ansteuerung_bhkw(
        Stoerung, Schalter, Wartungsmeldung, Thermische_Desinfektion, beispiel_daten
    )
    print(f"Schaltbefehl: {schaltbefehl}")
