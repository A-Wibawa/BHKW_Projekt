def berechnung_waermeleistung(
    vorlauftemp: float,
    ruecklauftemp: float,
    volumenstrom_m3h: float,
    dichte: float = 1000.0,
    cp: float = 4184.0
) -> float:
    """
    Berechnet die Wärmeleistung (kW) eines Heizkreises aus:
      • Vorlauftemperatur (°C)
      • Rücklauftemperatur (°C)
      • Volumenstrom (m³/h)

    Standardmäßig wird Wasser mit Dichte 1000 kg/m³ und
    spezifischer Wärmekapazität 4184 J/(kg·K) angenommen.

    Rückgabe:
      Wärmeleistung in Kilowatt (kW).

    Formel:
      Q_dot = m_dot * cp * ΔT
      m_dot = ρ * V_dot
      V_dot (m³/s) = volumenstrom_m3h / 3600
      => Q_dot [W] = ρ * (V_dot) * cp * (T_vor - T_rück)
      => Q_dot [kW] = Q_dot [W] / 1000
    """

    # 1. Temperaturdifferenz
    delta_t = vorlauftemp - ruecklauftemp
    if delta_t <= 0:
        raise ValueError("Vorlauftemperatur muss größer als Rücklauftemperatur sein.")

    # 2. Volumenstrom von m³/h in m³/s umrechnen
    volumens_m3s = volumenstrom_m3h / 3600.0

    # 3. Masseströmung (kg/s)
    masse_mdot = dichte * volumens_m3s

    # 4. Wärmeleistung in Watt
    waermeleistung_w = masse_mdot * cp * delta_t

    # 5. Umrechnung in kW
    waermeleistung_kw = waermeleistung_w / 1000.0

    return waermeleistung_kw



def plot_waermeleistung_zeitverlauf(
    timestamps: List[datetime],
    vorlauf_temps: List[float],
    ruecklauf_temps: List[float],
    volumenstrom_m3h: List[float],
    dichte: float = 1000.0,
    cp: float = 4184.0
) -> None:
    """
    Plottet die Wärmeleistung (kW) über gegebene Zeitpunkte.

    :param timestamps: Liste von datetime-Objekten.
    :param vorlauf_temps: Liste von Vorlauftemperaturen (°C).
    :param ruecklauf_temps: Liste von Rücklauftemperaturen (°C).
    :param volumenstrom_m3h: Liste von Volumenstrom-Werten (m³/h).
    """
    leisten = []
    for v, r, qv in zip(vorlauf_temps, ruecklauf_temps, volumenstrom_m3h):
        leisten.append(berechnung_waermeleistung(v, r, qv, dichte, cp))
    
    plt.figure()
    plt.plot(timestamps, leisten)
    plt.xlabel("Zeit")
    plt.ylabel("Wärmeleistung (kW)")
    plt.title("Wärmeleistung über Zeit")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # Beispielaufruf
    tv = 60.0    # Vorlauftemperatur in °C
    tr = 40.0    # Rücklauftemperatur in °C
    qv = 2.5     # Volumenstrom in m³/h

    leistung = berechnung_waermeleistung(tv, tr, qv)
    print(f"Wärmeleistung: {leistung:.2f} kW")
