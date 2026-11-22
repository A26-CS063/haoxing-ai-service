"""Latih dan bandingkan model saran level Shuo dari 6 poin rubrik penilaian laoshi.

Jalankan:  python -m src.train_level
Hasil: models/level_model.joblib, models/metrics.json, docs/model_comparison.md
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.preprocess import FEATURES, TARGET, load_clean

ROOT = Path(__file__).resolve().parent.parent
SEED = 42


def main():
    data = ROOT / "data/raw/rubrik_shuo_sintetis.csv"
    if not data.exists():  # data tiruan dibuat otomatis bila belum ada
        from src.make_dummy_rubrik import build
        data.parent.mkdir(parents=True, exist_ok=True)
        build().to_csv(data, index=False)
    df = load_clean(data)
    X, y = df[FEATURES], df[TARGET].astype(object)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)

    candidates = {
        "Baseline (kelas mayoritas)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")),
        "Random Forest": RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=SEED),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    rows, fitted = [], {}
    for name, model in candidates.items():
        cv_f1 = cross_val_score(model, X_tr, y_tr, cv=cv, scoring="f1_macro").mean()
        model.fit(X_tr, y_tr)
        pred = model.predict(X_te)
        rows.append({
            "model": name,
            "cv_f1_macro": round(float(cv_f1), 3),
            "test_accuracy": round(float(accuracy_score(y_te, pred)), 3),
            "test_f1_macro": round(float(f1_score(y_te, pred, average="macro")), 3),
        })
        fitted[name] = model

    real = [r for r in rows if not r["model"].startswith("Baseline")]
    best = max(real, key=lambda r: (r["cv_f1_macro"], r["test_f1_macro"]))
    final = candidates[best["model"]].fit(X, y)  # latih ulang di seluruh data untuk deployment

    (ROOT / "models").mkdir(exist_ok=True)
    joblib.dump({"model": final, "features": FEATURES, "name": best["model"], "data": "sintetis"}, ROOT / "models/level_model.joblib")
    (ROOT / "models/metrics.json").write_text(json.dumps({"results": rows, "best": best["model"],
        "n_train": len(X_tr), "n_test": len(X_te), "class_counts": y.value_counts().to_dict()}, indent=2))

    md = ["| Model | CV F1-macro (5-fold, data latih) | Akurasi (data uji) | F1-macro (data uji) |", "|---|---|---|---|"]
    md += [f"| {r['model']} | {r['cv_f1_macro']} | {r['test_accuracy']} | {r['test_f1_macro']} |" for r in rows]
    md += ["", f"Model terpilih: **{best['model']}** (CV F1-macro tertinggi di antara model non-baseline).",
           "", "Catatan: model ini dilatih dengan data TIRUAN (`data/raw/rubrik_shuo_sintetis.csv`), jadi angka di atas",
           "hanya menunjukkan alur berjalan, bukan kualitas di data nyata. Latih ulang setelah data penilaian laoshi terkumpul."]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/model_comparison.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
