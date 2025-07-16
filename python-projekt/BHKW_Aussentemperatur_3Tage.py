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


if __name__ == "__main__":
    # Beispiel-Daten: pro Tag drei Messwerte (07:00, 14:00, 21:00)
    beispiel_daten = {
        1: [15.2, 20.1, 17.4],
        2: [16.0, 21.3, 18.7],
        3: [14.8, 19.5, 17.0],
    }

    # Funktion aufrufen und Ergebnis speichern
    durchschnitt = berechnung_3_tage_mittelwert(beispiel_daten)
