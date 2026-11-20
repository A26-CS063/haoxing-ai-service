"""Uji penolakan pertanyaan di luar topik (Side Quest AE).

Dijalankan dalam mode fallback (tanpa kunci Gemini) supaya hasilnya pasti dan tidak
memanggil layanan luar. Pencarian dokumen masih leksikal (TF-IDF), sehingga ada
kasus yang belum tertangani (ditandai xfail). Perbaikan tuntasnya: pencarian
berbasis embedding (RAG), karena kata seperti "Jakarta" atau "Indonesia" juga
muncul di profil pengajar dan "pengajarnya" tidak dikenali sebagai "pengajar".
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

# Lolos ke jawaban walau di luar topik karena kata yang sama ada di dokumen FAQ.
BELUM_DITOLAK = {
    "Siapa presiden Indonesia sekarang?",
    "Tolong buatkan kode Python untuk sorting",
    "Bagaimana cuaca besok di Jakarta?",
}

ON_TOPIC = [
    "Berapa harga HSK 1?",
    "Apa itu kelas Shuo?",
    "Apakah ada refund?",
    "Berapa biaya paket lancar ngomong?",
    "Kapan kelas dibuka?",
    "Berapa harga Shuo online level 3?",
    "Apakah bisa bayar pakai QRIS?",
    "Berapa lama durasi kelas?",
    "Apakah ada asrama?",
    "Apakah refund bisa kalau belum mulai kelas?",
]

# Pertanyaan sah yang belum ditemukan karena tidak ada kata yang sama persis.
BELUM_DITEMUKAN = ["Siapa saja pengajarnya?"]


def _tandai(daftar, bermasalah, alasan):
    return [
        pytest.param(q, marks=pytest.mark.xfail(reason=alasan)) if q in bermasalah else q
        for q in daftar
    ]


@pytest.fixture(autouse=True)
def tanpa_kunci(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


@pytest.mark.parametrize(
    "q", _tandai(OFF_TOPIC, BELUM_DITOLAK, "pencarian leksikal; butuh RAG embedding")
)
def test_di_luar_topik_ditolak(q):
    r = client.post("/api/v1/faq", json={"pertanyaan": q})
    assert r.status_code == 200
    body = r.json()
    assert body["jawaban"] == OFF_TOPIC_MSG
    assert body["sumber"] == []


@pytest.mark.parametrize(
    "q",
    _tandai(ON_TOPIC + BELUM_DITEMUKAN, set(BELUM_DITEMUKAN), "tanpa stemming; butuh RAG embedding"),
)
def test_dalam_topik_dijawab(q):
    r = client.post("/api/v1/faq", json={"pertanyaan": q})
    assert r.status_code == 200
    body = r.json()
    assert body["jawaban"] != OFF_TOPIC_MSG
    assert body["sumber"]
