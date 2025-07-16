import matplotlib.pyplot as plt

# --- Konstanten ---
cp = 4180           # spezifische Wärmekapazität [J/kg·K]
rho = 1000          # Dichte Wasser [kg/m³]
V_dot = 0.5         # Volumenstrom [m³/h]
T_ruecklauf = 30.0  # Rücklauftemperatur [°C]

# --- Massenstrom berechnen ---
m_dot = V_dot * rho / 3600  # [kg/s]

# --- Beispielhafte Heizlast in W pro Stunde (24h-Tagesverlauf) ---
Q_heizlast = [
    6000, 5800, 5600, 5400, 5200, 5000, 4800, 4600, 4000, 3500, 3200, 3000,
    2800, 2700, 2600, 2500, 3000, 4000, 4500, 5000, 5500, 5800, 6000, 6200
]

# --- Vorlauftemperatur berechnen ---
T_vorlauf = [(Q / (m_dot * cp)) + T_ruecklauf for Q in Q_heizlast]

# --- Ausgabe + Plot ---
for stunde, (Q, T_vl) in enumerate(zip(Q_heizlast, T_vorlauf)):
    print(f"{stunde:02d}:00 - Heizlast: {Q:4.0f} W → Vorlauf: {T_vl:.2f} °C")

# Plot
plt.figure(figsize=(10, 5))
plt.plot(range(24), T_vorlauf, marker='o')
plt.title("Vorlauftemperatur über 24h bei stündlich variierender Heizlast")
plt.xlabel("Stunde des Tages")
plt.ylabel("Vorlauftemperatur [°C]")
plt.grid(True)
plt.xticks(range(0, 24))
plt.tight_layout()
plt.show()
	