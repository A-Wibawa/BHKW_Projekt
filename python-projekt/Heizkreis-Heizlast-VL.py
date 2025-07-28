import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def _parse_datetime(s: str) -> pd.Timestamp:
    """Versucht, einen Zeitstempel in ISO- oder deutschem Format zu parsen."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M"):
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except ValueError:
            continue
    return pd.NaT

def berechne_heizlast_und_vorlauftemperatur(
    weather_csv: str,
    UA: float,
    T_in_set: float,
    V_dot: float,
    T_ruecklauf: float,
    cp: float = 4180,
    rho: float = 1000
) -> pd.DataFrame:
    # CSV einlesen und Zeitstempel parsen
    df = pd.read_csv(
        weather_csv,
        sep=";",
        names=["DateTime", "TempRaw"],
        header=0,
        encoding="latin1",
        engine="python",
    )
    df["DateTime"] = df["DateTime"].astype(str).apply(_parse_datetime)
    df = df.dropna(subset=["DateTime"]).set_index("DateTime")
    df = df[~df.index.duplicated(keep="first")]

    # Rohwerte in °C umwandeln
    df["T_out"] = (
        df["TempRaw"]
        .astype(str)
        .str.replace(r"[^0-9]", "", regex=True)
        .astype(float)
        / 1000.0
    )

    # auf stündliche Frequenz bringen und fehlende Werte interpolieren
    df = df[["T_out"]].asfreq("h").interpolate()

    # Heizlast (W) berechnen
    df["Q_heiz"] = (UA * (T_in_set - df["T_out"])).clip(lower=0.0)

    # Massenstrom [kg/s]
    m_dot = V_dot * rho / 3600.0

    # Vorlauftemperatur (°C) berechnen
    df["T_vorlauf"] = df["Q_heiz"] / (m_dot * cp) + T_ruecklauf

    return df

# ---------- Beispielaufruf ----------
weather_file = "Woche.csv"
UA = 300.0
T_set = 20.0
V_dot = 0.5
T_rueck = 30.0

df_res = berechne_heizlast_und_vorlauftemperatur(
    weather_file, UA, T_set, V_dot, T_rueck
)

# 1) Ausgabe der ersten 24 Stunden
print(df_res.head(24))

# 2) Plot: Außen- vs. Soll-Vorlauftemperatur mit täglichen Ticks
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_res.index, df_res["T_out"],      label="T_out")
ax.plot(df_res.index, df_res["T_vorlauf"],  label="T_vorlauf")

ax.set_xlabel("Datum")
ax.set_ylabel("Temperatur [°C]")
ax.set_title("Außen- vs. Soll-Vorlauftemperatur")
ax.legend()
ax.grid(True)

# tägliche Major-Ticks
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3) Plot: Heizlastverlauf mit täglichen Ticks
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_res.index, df_res["Q_heiz"], label="Q_heiz")

ax.set_xlabel("Datum")
ax.set_ylabel("Heizlast [W]")
ax.set_title("Heizlastverlauf")
ax.legend()
ax.grid(True)

# tägliche Major-Ticks
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
