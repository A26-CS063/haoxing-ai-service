"""Uji jalur Gemini tanpa memanggil layanan luar (httpx.post diganti tiruan)."""
import httpx
import pytest

from src.app import faq as faq_mod
from src.app.faq import FaqEngine

PERTANYAAN = "Berapa harga HSK 1?"


class Balasan:
    def __init__(self, kode, teks="Jawaban Gemini"):
        self.status_code = kode
        self._teks = teks

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("gagal", request=None, response=self)

    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": self._teks}]}}]}


@pytest.fixture(autouse=True)
def kunci_palsu(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "kunci-uji")
    monkeypatch.setattr(faq_mod.time, "sleep", lambda s: None)


def test_berhasil_generative(monkeypatch):
    monkeypatch.setattr(faq_mod.httpx, "post", lambda *a, **k: Balasan(200))
    hasil = FaqEngine().answer(PERTANYAAN)
    assert hasil["mode"] == "generative"
    assert hasil["jawaban"] == "Jawaban Gemini"


def test_ulang_sekali_saat_gemini_sibuk(monkeypatch):
    urutan = [Balasan(503), Balasan(200)]
    monkeypatch.setattr(faq_mod.httpx, "post", lambda *a, **k: urutan.pop(0))
    assert FaqEngine().answer(PERTANYAAN)["mode"] == "generative"


def test_fallback_jika_tetap_gagal(monkeypatch):
    monkeypatch.setattr(faq_mod.httpx, "post", lambda *a, **k: Balasan(503))
    assert FaqEngine().answer(PERTANYAAN)["mode"] == "fallback"


def test_fallback_saat_timeout(monkeypatch):
    def timeout(*a, **k):
        raise httpx.ReadTimeout("lambat")

    monkeypatch.setattr(faq_mod.httpx, "post", timeout)
    assert FaqEngine().answer(PERTANYAAN)["mode"] == "fallback"
