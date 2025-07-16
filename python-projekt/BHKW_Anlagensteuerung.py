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

# Beispielaufruf
if __name__ == "__main__":
    Stoerung = False
    Schalter = True
    Wartungsmeldung = False
    Thermische_Desinfektion = False

    # Die Funktion gibt den Status zurück, den wir hier ausgeben
    status = anlagensteuerung_bhkw(
        Stoerung,
        Schalter,
        Wartungsmeldung,
        Thermische_Desinfektion
    )
    print(status)