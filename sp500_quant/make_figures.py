#!/usr/bin/env python3
"""make_figures.py — Figuras del informe a partir de resultados/*.csv"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

here = os.path.dirname(os.path.abspath(__file__))
res = os.path.join(here, "resultados")
fig_dir = os.path.join(res, "figuras")
os.makedirs(fig_dir, exist_ok=True)

BASE21, BASE63 = 0.5799, 0.6330
fs, axs = plt.subplots(2, 2, figsize=(13, 9))

# --- 1. Hit ratio 21d por quintil (varias señales) ---
ax = axs[0, 0]
for name, lab in [("dist_52w_high", "Dist. a máx. 52s"),
                  ("volatility_level", "Volatilidad 21d"),
                  ("volume_ratio", "Volumen/media 20d"),
                  ("composite_signal", "Score compuesto")]:
    d = pd.read_csv(os.path.join(res, f"{name}.csv"))
    ax.plot(d["q"], d["hit21"] * 100, marker="o", label=lab)
ax.axhline(BASE21 * 100, color="k", ls="--", lw=1, label="Tasa base (57.99%)")
ax.set_title("P(sube en 21d) por quintil — señales cross-sectional")
ax.set_xlabel("Quintil (1 = más bajo en la señal)")
ax.set_ylabel("Hit ratio 21d (%)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- 2. Hit ratio 63d por quintil ---
ax = axs[0, 1]
for name, lab in [("dist_52w_high", "Dist. a máx. 52s"),
                  ("volatility_compression", "Compresión de vol."),
                  ("composite_signal", "Score compuesto")]:
    d = pd.read_csv(os.path.join(res, f"{name}.csv"))
    ax.plot(d["q"], d["hit63"] * 100, marker="o", label=lab)
ax.axhline(BASE63 * 100, color="k", ls="--", lw=1, label="Tasa base (63.30%)")
ax.set_title("P(sube en 63d) por quintil")
ax.set_xlabel("Quintil")
ax.set_ylabel("Hit ratio 63d (%)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- 3. Eventos extremos ---
ax = axs[1, 0]
d = pd.read_csv(os.path.join(res, "extreme_down_events.csv"))
d = d[d["estado"] != "resto"].sort_values("hit21")
ax.barh(d["estado"], (d["hit21"] - BASE21) * 100, color="steelblue", label="21d")
ax.barh(d["estado"], (d["hit63"] - BASE63) * 100, height=0.4,
        color="darkorange", alpha=0.8, label="63d")
ax.axvline(0, color="k", lw=1)
ax.set_title("Exceso de P(suba) tras caídas extremas (vs. tasa base, pp)")
ax.set_xlabel("Diferencia en puntos porcentuales")
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis="x")

# --- 4. Autocorrelación mensual por símbolo ---
ax = axs[1, 1]
ac = pd.read_csv(os.path.join(res, "autocorrelation_por_simbolo.csv"))
ax.hist(ac["ac1_m"].dropna(), bins=40, color="seagreen", alpha=0.85)
ax.axvline(0, color="k", lw=1)
ax.axvline(ac["ac1_m"].mean(), color="red", ls="--",
           label=f"media = {ac['ac1_m'].mean():.3f}")
ax.set_title("Autocorrelación mensual de retornos (496 tickers)")
ax.set_xlabel("AC(1) mensual")
ax.set_ylabel("nº de tickers")
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(fig_dir, "patrones_sp500.png")
plt.savefig(out, dpi=110)
print("figura ->", out)
