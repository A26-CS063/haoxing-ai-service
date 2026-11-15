"""Preprocessing data pre-test untuk model rekomendasi tingkat."""
import re
import pandas as pd

FEATURES = ["skor_pretest", "skor_listening", "skor_grammar"]
LEVELS = ["Basic", "Tingkat 1", "Tingkat 2", "Tingkat 3", "Tingkat 4"]


def to_tingkat(label: str) -> str:
    """Petakan label jalur+tingkat (mis. 'Grammar 2', 'HSK 4B', 'Shuo Basic') ke tingkat saja.

    Alasan: skor pre-test memakai rentang sama untuk jalur HSK, Grammar, dan Shuo,
    sehingga jalur tidak dapat diprediksi dari skor. Jalur dipilih admin.
    """
    if "Basic" in label:
        return "Basic"
    m = re.search(r"(\d)", label)
    if not m:
        raise ValueError(f"Label tidak dikenali: {label}")
    return f"Tingkat {m.group(1)}"


def load_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="student_id")
    df = df.dropna(subset=FEATURES + ["recommended_level"])
    for c in FEATURES:
        df = df[df[c].between(0, 100)]
    df = df.assign(tingkat=df["recommended_level"].map(to_tingkat))
    return df.reset_index(drop=True)
