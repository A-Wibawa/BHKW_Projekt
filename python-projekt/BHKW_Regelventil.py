import matplotlib.pyplot as plt

# --- PID Parameter ---
Kp = 2.0
Ki = 0.15
Kd = 0.0  # Kein D-Anteil für Stabilität

# --- Systemparameter ---
T_kessel = 95
T_ruecklauf = 30.0
T_ist = 28.0

# --- Regler-Einstellungen ---
dt = 1.0
sim_time = 400
totzone = 0.3
reset_band = 0.2
traegheit = 0.04

# --- Sollwertprofil ---
def sollwert(t):
    return 42.0 #if t < 200 else 47.0

# --- Initialisierung ---
integral = max(min(integral, 100), -100)
last_error = 0.0
temps = []
ventil_oeffnung = []
sollwerte = []
stellwert = 0.0

# --- Simulation ---
for t in range(int(sim_time)):
    T_soll = sollwert(t)
    error = T_soll - T_ist
    sollwerte.append(T_soll)

    if abs(error) < totzone:
        error = 0.0
    if abs(error) > reset_band:
        integral += error * dt

    derivative = (error - last_error) / dt
    last_error = error

    raw_stellwert = Kp * error + Ki * integral + Kd * derivative
    raw_stellwert = max(0, min(100, raw_stellwert))

    max_delta = 5.0
    delta = raw_stellwert - stellwert
    delta = max(-max_delta, min(max_delta, delta))
    stellwert += delta

    alpha = stellwert / 100.0
    T_gemischt = alpha * T_kessel + (1 - alpha) * T_ruecklauf
    T_ist += (T_gemischt - T_ist) * traegheit

    temps.append(T_ist)
    ventil_oeffnung.append(stellwert)

# --- Einschwingzeit-Funktion ---
def berechne_einschwingzeit(start_index, zielwert, toleranz=0.5, stabil_dauer=30):
    for i in range(start_index, len(temps)):
        if abs(temps[i] - zielwert) <= toleranz:
            if all(abs(temps[j] - zielwert) <= toleranz for j in range(i, min(i + stabil_dauer, len(temps)))):
                return i
    return None

einschwing_1 = berechne_einschwingzeit(0, 40.0)
einschwing_2 = berechne_einschwingzeit(200, 45.0)

# --- Ausgabe Einschwingzeit + Ventilstellung ---
#print("\n📊 Einschwingzeiten:")
#if einschwing_1 is not None:
    print(f"✅ Einschwingzeit auf 40 °C: {einschwing_1} Sekunden")
#else:
#    print("❌ Keine stabile Einschwingung auf 40 °C")

#if einschwing_2 is not None:
#    print(f"✅ Einschwingzeit auf 45 °C (nach Sprung): {einschwing_2 - 200} Sekunden (ab Sekunde 200)")
#else:
#    print("❌ Keine stabile Einschwingung auf 45 °C")

# 🔧 Ventilstellung am Ende:
print(f"\n🟢 Letzte Ventilöffnung: {ventil_oeffnung[-1]:.1f} %")

# --- Plot mit Legenden ---
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.set_title("PID-Regelung - Regelventil")
ax1.set_xlabel("Zeit [s]")
ax1.set_ylabel("T_vorlauf [°C]", color='tab:blue')
l1 = ax1.plot(temps, label="Vorlauftemperatur (Ist)", color='tab:blue')
l2 = ax1.plot(sollwerte, label="Vorlauftemperatur (Soll)", linestyle='--', color='red')

ax2 = ax1.twinx()
ax2.set_ylabel("Ventilöffnung [%]", color='tab:green')
l3 = ax2.plot(ventil_oeffnung, label="Ventilöffnung", color='tab:green')

# Kombinierte Legende
lines = l1 + l2 + l3
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc="upper left")

ax1.grid(True)
fig.tight_layout()
plt.show()
