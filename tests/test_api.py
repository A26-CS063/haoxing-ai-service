import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def trained():
    if not (ROOT / "models/level_model.joblib").exists():
        subprocess.run([sys.executable, "-m", "src.train_level"], cwd=ROOT, check=True)


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from src.app.main import app
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_predict_low_and_high(client):
    low = client.post("/api/v1/predict-level", json={"skor_pretest": 35, "skor_listening": 30, "skor_grammar": 38}).json()
    high = client.post("/api/v1/predict-level", json={"skor_pretest": 95, "skor_listening": 92, "skor_grammar": 97}).json()
    assert low["tingkat"] == "Basic"
    assert high["tingkat"] == "Tingkat 4"
    assert abs(sum(high["probabilitas"].values()) - 1) < 0.01


@pytest.mark.parametrize("body", [
    {"skor_pretest": 120, "skor_listening": 50, "skor_grammar": 50},
    {"skor_pretest": -1, "skor_listening": 50, "skor_grammar": 50},
    {"skor_pretest": 50, "skor_listening": 50},
    {"skor_pretest": "abc", "skor_listening": 50, "skor_grammar": 50},
])
def test_predict_invalid_input(client, body):
    assert client.post("/api/v1/predict-level", json=body).status_code == 422


def test_faq_in_context(client):
    r = client.post("/api/v1/faq", json={"pertanyaan": "Berapa harga Shuo Online Basic?"}).json()
    assert "250.000" in r["jawaban"] and r["mode"] == "fallback"


def test_faq_off_topic(client):
    r = client.post("/api/v1/faq", json={"pertanyaan": "Siapa presiden Amerika?"}).json()
    assert "belum tersedia" in r["jawaban"]


def test_faq_empty_rejected(client):
    assert client.post("/api/v1/faq", json={"pertanyaan": ""}).status_code == 422
