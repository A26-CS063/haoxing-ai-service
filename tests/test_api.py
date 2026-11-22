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


def test_faq_in_context(client):
    r = client.post("/api/v1/faq", json={"pertanyaan": "Berapa harga Shuo Online Basic?"}).json()
    assert "250.000" in r["jawaban"] and r["mode"] == "fallback"


def test_faq_off_topic(client):
    r = client.post("/api/v1/faq", json={"pertanyaan": "Siapa presiden Amerika?"}).json()
    assert "belum tersedia" in r["jawaban"]


def test_faq_empty_rejected(client):
    assert client.post("/api/v1/faq", json={"pertanyaan": ""}).status_code == 422
