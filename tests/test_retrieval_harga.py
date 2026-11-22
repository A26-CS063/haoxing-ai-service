"""Pencegah regresi: pertanyaan biaya harus menemukan baris harga, bukan baris lain."""
from src.app.faq import FaqEngine


def test_biaya_hsk_menemukan_harga():
    ctx = FaqEngine().retrieve("Berapa biaya HSK 1?")
    assert any("Rp750.000" in c for c in ctx)


def test_biaya_grammar_menemukan_harga():
    ctx = FaqEngine().retrieve("Biaya Grammar level 3 berapa?")
    assert any("Rp400.000" in c for c in ctx)