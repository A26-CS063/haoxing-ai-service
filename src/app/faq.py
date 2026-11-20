"""Asisten FAQ: ambil konteks dari dokumen program (TF-IDF) lalu jawab dengan Gemini.

Jika GEMINI_API_KEY tidak ada atau layanan gagal, kembalikan kutipan konteks (mode fallback)
sehingga backend tetap mendapat jawaban yang jelas.
"""
import os
import re
from pathlib import Path

import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOC = Path(__file__).resolve().parents[2] / "data/faq/program_haoxing.md"
SYSTEM = (
    "Kamu asisten admin Haoxing Mandarin Center. Jawab singkat dalam Bahasa Indonesia HANYA "
    "berdasarkan konteks. Jika jawaban tidak ada di konteks atau pertanyaan di luar topik kursus, "
    "jawab sopan bahwa informasi tidak tersedia dan sarankan menghubungi admin."
)
OFF_TOPIC_MSG = "Maaf, informasi itu belum tersedia. Silakan hubungi admin Haoxing Mandarin Center."


def _chunks() -> list[str]:
    text = DOC.read_text(encoding="utf-8")
    parts = [p.strip() for p in re.split(r"\n(?=## )", text) if p.strip() and not p.strip().startswith("# ")]
    out = []
    for p in parts:
        lines = p.splitlines()
        head = lines[0]
        out += [f"{head} | {l.lstrip('- ').strip()}" for l in lines[1:] if l.strip().startswith("-")] or [p]
    return out


class FaqEngine:
    def __init__(self):
        self.chunks = _chunks()
        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.mat = self.vec.fit_transform(self.chunks)

    def retrieve(self, q: str, k: int = 4, min_score: float = 0.15):
        sims = cosine_similarity(self.vec.transform([q]), self.mat)[0]
        idx = sims.argsort()[::-1][:k]
        return [self.chunks[i] for i in idx if sims[i] >= min_score]

    def answer(self, q: str) -> dict:
        ctx = self.retrieve(q)
        if not ctx:
            return {"jawaban": OFF_TOPIC_MSG, "sumber": [], "mode": "fallback"}
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if key:
            try:
                return {"jawaban": self._gemini(q, ctx, key), "sumber": ctx, "mode": "generative"}
            except Exception as e:
                print(f"[faq] Gemini gagal, pakai fallback: {type(e).__name__} {getattr(getattr(e, 'response', None), 'status_code', '')}")  # tanpa kunci/URL
        return {"jawaban": "Informasi yang ditemukan: " + "; ".join(ctx), "sumber": ctx, "mode": "fallback"}

    def _gemini(self, q: str, ctx: list[str], key: str) -> str:
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        prompt = f"{SYSTEM}\n\nKonteks:\n" + "\n".join(f"- {c}" for c in ctx) + f"\n\nPertanyaan: {q}\nJawaban:"
        r = httpx.post(url, headers={"x-goog-api-key": key}, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
