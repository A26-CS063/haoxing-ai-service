"""Uji /api/v1/predict-level (rubrik 6 poin -> saran level Shuo) dan hitungan nilai akhir."""
import pytest
from fastapi.testclient import TestClient

from src.preprocess import LEVELS, kategori, nilai_akhir

SEMUA = ["pelafalan", "kelancaran", "tata_bahasa", "kosakata", "nada", "komunikasi"]


def body(nilai):
    return {k: nilai for k in SEMUA}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from src.app.main import app
    return TestClient(app)


def test_skor_rendah_dan_tinggi(client):
    rendah = client.post("/api/v1/predict-level", json=body(45)).json()
    tinggi = client.post("/api/v1/predict-level", json=body(95)).json()
    assert rendah["level_saran"] == "Shuo 1"
    assert tinggi["level_saran"] == "Shuo 5"
    assert set(tinggi["probabilitas"]) == set(LEVELS)
    assert abs(sum(tinggi["probabilitas"].values()) - 1) < 0.01


def test_bentuk_respons(client):
    r = client.post("/api/v1/predict-level", json={
        "pelafalan": 80, "kelancaran": 75, "tata_bahasa": 70, "kosakata": 65, "nada": 70, "komunikasi": 60}).json()
    assert r["nilai_akhir"] == 71.0
    assert r["kategori"] == "Good"
    assert "laoshi" in r["catatan"]
    assert r["level_saran"] in LEVELS


def test_nilai_akhir_berbobot():
    # 20% x4 poin, 10% x2 poin
    assert nilai_akhir({"pelafalan": 100, "kelancaran": 100, "tata_bahasa": 100, "kosakata": 100, "nada": 0, "komunikasi": 0}) == 80.0


@pytest.mark.parametrize("nilai,hasil", [
    (100, "Excellent"), (90, "Excellent"), (89.9, "Very Good"), (80, "Very Good"),
    (79.9, "Good"), (70, "Good"), (69.9, "Fair"), (60, "Fair"), (59.9, "Needs Improvement"), (0, "Needs Improvement"),
])
def test_kategori(nilai, hasil):
    assert kategori(nilai) == hasil


@pytest.mark.parametrize("data", [
    {**body(50), "pelafalan": 120},
    {**body(50), "nada": -1},
    {k: 50 for k in SEMUA[:-1]},                      # satu poin hilang
    {**body(50), "kosakata": "abc"},
    {"skor_pretest": 72, "skor_listening": 65, "skor_grammar": 78},  # format lama ditolak
])
def test_input_tidak_valid(client, data):
    assert client.post("/api/v1/predict-level", json=data).status_code == 422
