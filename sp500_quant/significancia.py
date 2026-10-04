#!/usr/bin/env python3
"""
significancia.py — Contrasta cada hit ratio condicional contra la tasa base
incondicional (test de diferencia de proporciones, z de dos colas) y añade
IC95% de Wilson. Genera tablas listas para el informe.
"""
from __future__ import annotations

import json
import math
import os

import pandas as pd


def wilson(k: float, n: float, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def vs_base(hit: float, n: float, base: float) -> tuple[float, float]:
    """z y p (dos colas) de H0: hit == base."""
    if not n or math.isnan(hit):
        return (float("nan"), float("nan"))
    se = math.sqrt(base * (1 - base) / n)
    if se == 0:
        return (float("nan"), float("nan"))
    z = (hit - base) / se
    p = math.erfc(abs(z) / math.sqrt(2))
    return (z, p)


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "resultados")
    r = json.load(open(os.path.join(out, "resumen.json")))
    base21 = r["extras"]["base_rates"]["hit21"]
    base63 = r["extras"]["base_rates"]["hit63"]
    base5 = r["extras"]["base_rates"]["hit5d"]
    print(f"Tasa base incondicional: P(sube 21d)={base21:.4f}  P(sube 63d)={base63:.4f}\n")

    filas = []

    def add(patron, bucket, n, hit, horizonte):
        base = {5: base5, 21: base21, 63: base63}[horizonte]
        lo, hi = wilson(hit * n, n)
        z, p = vs_base(hit, n, base)
        filas.append({
            "patron": patron, "bucket": bucket, "horizonte_d": horizonte, "n": int(n),
            "hit": hit, "hit_lo95": lo, "hit_hi95": hi,
            "base": base, "delta_pp": (hit - base) * 100,
            "z": z, "p_valor": p,
            "significativo_5%": "sí" if (p == p and p < 0.05) else "no",
        })

    def scan(name, bucket_col, hit_col="hit21", horizonte=21, prefijo=""):
        for row in r["queries"].get(name, []):
            add(prefijo + name, str(row.get(bucket_col)), row.get("n"), row.get(hit_col), horizonte)

    scan("volatility_level", "q")
    scan("volatility_compression", "q", "hit63", 63)
    scan("dist_52w_high", "q")
    scan("dist_52w_high", "q", "hit63", 63)
    scan("new_52w_high_event", "estado")
    scan("breakout_20d", "estado")
    scan("trend_sma", "estado")
    scan("trend_sma", "estado", "hit63", 63)
    scan("volume_ratio", "q")
    scan("composite_signal", "q")
    scan("composite_signal", "q", "hit63", 63)
    scan("extreme_down_events", "estado")
    scan("extreme_down_events", "estado", "hit63", 63)
    scan("short_term_reversal", "q", "hit5", 5)
    for row in r["queries"].get("monthly_signals", []):
        add("monthly_" + row["señal"], row["bucket"], row["n"], row["hit"], 21)

    df = pd.DataFrame(filas).sort_values(["patron", "horizonte_d", "bucket"])
    df.to_csv(os.path.join(out, "significancia_vs_base.csv"), index=False)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print(df.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
