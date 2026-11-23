"""Uji susunan prompt Gemini (template terstruktur + few-shot), tanpa memanggil layanan luar."""
from src.app.faq import OFF_TOPIC_MSG, _prompt


def test_prompt_memuat_aturan_contoh_dan_pertanyaan():
    p = _prompt("Berapa biaya HSK 2?", ["Kelas HSK | HSK 2: Rp850.000"])
    assert "ATURAN" in p and "CONTOH FORMAT" in p
    assert OFF_TOPIC_MSG in p
    assert "- Kelas HSK | HSK 2: Rp850.000" in p
    assert p.rstrip().endswith("Pertanyaan: Berapa biaya HSK 2?\nJawaban:")


def test_pertanyaan_nyata_setelah_contoh():
    p = _prompt("Halo?", ["TEKS-KONTEKS-UJI"])
    assert p.index("SEKARANG JAWAB") > p.index("CONTOH FORMAT")
    assert p.index("TEKS-KONTEKS-UJI") > p.index("SEKARANG JAWAB")