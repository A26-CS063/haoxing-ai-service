"""Preprocessing data penilaian laoshi (rubrik 6 poin) untuk model saran level Shuo.

Sumber rubrik: "Rubrik Penilaian Kelas Speaking" Haoxing Mandarin Center.
Tiap poin dinilai 0-100; nilai akhir = rata-rata berbobot.
"""
import pandas as pd

# Urutan sesuai rubrik. Bobot dalam persen (total 100).
BOBOT = {
    "pelafalan": 20,
    "kelancaran": 20,
    "tata_bahasa": 20,
    "kosakata": 20,
    "nada": 10,
    "komunikasi": 10,
}
FEATURES = list(BOBOT)
LEVELS = ["Shuo 1", "Shuo 2", "Shuo 3", "Shuo 4", "Shuo 5"]
TARGET = "level"


def nilai_akhir(skor: dict[str, float]) -> float:
    """Rata-rata berbobot dari 6 poin rubrik (skala 0-100)."""
    return sum(skor[f] * BOBOT[f] for f in FEATURES) / sum(BOBOT.values())


def kategori(nilai: float) -> str:
    """Kategori nilai menurut rubrik Haoxing."""
    if nilai >= 90:
        return "Excellent"
    if nilai >= 80:
        return "Very Good"
    if nilai >= 70:
        return "Good"
    if nilai >= 60:
        return "Fair"
    return "Needs Improvement"


def load_clean(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="id")
    df = df.dropna(subset=FEATURES + [TARGET])
    for c in FEATURES:
        df = df[df[c].between(0, 100)]
    df = df[df[TARGET].isin(LEVELS)]
    return df.reset_index(drop=True)
