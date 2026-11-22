"""Buat data TIRUAN (sintetis) rubrik 6 poin + level Shuo untuk menjalankan alur model.

Jalankan:  python -m src.make_dummy_rubrik
Hasil: data/raw/rubrik_shuo_sintetis.csv

PENTING: ini bukan data siswa asli. Dipakai sementara sampai data penilaian laoshi
(skor 6 poin + level final) terkumpul dari aplikasi atau diganti data dari tim DS.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.preprocess import FEATURES, LEVELS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/raw/rubrik_shuo_sintetis.csv"
SEED = 42
N_PER_LEVEL = 120
# Rata-rata kemampuan umum per level, lalu tiap poin menyimpang acak.
MU = {"Shuo 1": 52, "Shuo 2": 61, "Shuo 3": 70, "Shuo 4": 78, "Shuo 5": 86}
SD_SISWA = 6.0   # variasi kemampuan antar siswa dalam satu level
SD_POIN = 5.0    # variasi tiap poin rubrik pada siswa yang sama


def build() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for level in LEVELS:
        for _ in range(N_PER_LEVEL):
            kemampuan = rng.normal(MU[level], SD_SISWA)
            skor = np.clip(rng.normal(kemampuan, SD_POIN, size=len(FEATURES)), 0, 100).round(0)
            rows.append({**dict(zip(FEATURES, skor.astype(int))), "level": level})
    df = pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)
    df.insert(0, "id", [f"SIM-{i + 1:04d}" for i in range(len(df))])
    return df


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build().to_csv(OUT, index=False)
    print(f"Tersimpan: {OUT}")
