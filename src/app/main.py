"""FastAPI: serving model rekomendasi level + asisten FAQ. Swagger di /docs."""
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.app.faq import FaqEngine
from src.preprocess import kategori, nilai_akhir
from src.app.schemas import FaqRequest, FaqResponse, PredictLevelRequest, PredictLevelResponse

load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="Haoxing AI Service", version="1.0.0",
              description="Saran level Shuo dari rubrik penilaian laoshi dan asisten FAQ (dipanggil oleh backend aplikasi).")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

_bundle = None
_faq = None


def bundle():
    global _bundle
    if _bundle is None:
        path = ROOT / "models/level_model.joblib"
        if not path.exists():
            raise HTTPException(503, "Model belum tersedia. Jalankan: python -m src.train_level")
        _bundle = joblib.load(path)
    return _bundle


def faq_engine():
    global _faq
    if _faq is None:
        _faq = FaqEngine()
    return _faq


@app.get("/", include_in_schema=False)
def root():
    return {"service": "Haoxing AI Service", "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "model_loaded": (ROOT / "models/level_model.joblib").exists()}


@app.post("/api/v1/predict-level", response_model=PredictLevelResponse, tags=["level"])
def predict_level(req: PredictLevelRequest):
    b = bundle()
    skor = {f: float(getattr(req, f)) for f in b["features"]}
    X = pd.DataFrame([skor], columns=b["features"])
    model = b["model"]
    proba = model.predict_proba(X)[0]
    classes = [str(c) for c in model.classes_]
    best = classes[int(proba.argmax())]
    total = nilai_akhir(skor)
    return PredictLevelResponse(
        level_saran=best,
        probabilitas={c: round(float(p), 3) for c, p in zip(classes, proba)},
        nilai_akhir=round(total, 1),
        kategori=kategori(total),
        catatan="Saran saja, keputusan akhir di laoshi",
        model=b["name"],
    )


@app.post("/api/v1/faq", response_model=FaqResponse, tags=["faq"])
def faq(req: FaqRequest):
    return faq_engine().answer(req.pertanyaan.strip())
