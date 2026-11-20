"""Uji penolakan pertanyaan di luar topik (Side Quest AE).

Dijalankan dalam mode fallback (tanpa kunci Gemini) supaya hasilnya pasti dan tidak
memanggil layanan luar. Ambang kemiripan (min_score) perlu dikalibrasi ulang jika
dokumen FAQ diganti dengan brosur asli.
"""
import pytest
from fastapi.testclient import TestClient

from src.app.faq import OFF_TOPIC_MSG
from src.app.main import app

client = TestClient(app)

OFF_TOPIC = [
    "Siapa presiden Indonesia sekarang?",
    "Bagaimana cara membuat nasi goreng?",
    "Berapa skor pertandingan sepak bola semalam?",
    "Tolong buatkan kode Python untuk sorting",
    "Apa ibu kota Prancis?",
    "Bagaimana cuaca besok di Jakarta?",
    "Berikan saran investasi saham yang bagus",
    "Ceritakan lelucon lucu",
    "Siapa pemenang piala dunia 2022?",
    "Bantu aku mengerjakan PR matematika",
]

ON_TOPIC = [
    "Berapa harga HSK 1?",
    "Apa itu kelas Shuo?",
    "Apakah ada refund?",
    "Berapa biaya paket lancar ngomong?",
]


@pytest.fixture(autouse=True)
def tanpa_kunci(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


@pytest.mark.parametrize("q", OFF_TOPIC)
def test_di_luar_topik_ditolak(q):
    r = client.post("/api/v1/faq", json={"pertanyaan": q})
    assert r.status_code == 200
    body = r.json()
    assert body["jawaban"] == OFF_TOPIC_MSG
    assert body["sumber"] == []


@pytest.mark.parametrize("q", ON_TOPIC)
def test_dalam_topik_dijawab(q):
    r = client.post("/api/v1/faq", json={"pertanyaan": q})
    assert r.status_code == 200
    body = r.json()
    assert body["jawaban"] != OFF_TOPIC_MSG
    assert body["sumber"]