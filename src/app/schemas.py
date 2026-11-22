from pydantic import BaseModel, Field


class PredictLevelRequest(BaseModel):
    """6 poin rubrik penilaian laoshi, masing-masing 0-100."""
    pelafalan: float = Field(ge=0, le=100)
    kelancaran: float = Field(ge=0, le=100)
    tata_bahasa: float = Field(ge=0, le=100)
    kosakata: float = Field(ge=0, le=100)
    nada: float = Field(ge=0, le=100)
    komunikasi: float = Field(ge=0, le=100)


class PredictLevelResponse(BaseModel):
    level_saran: str
    probabilitas: dict[str, float]
    nilai_akhir: float
    kategori: str
    catatan: str
    model: str


class FaqRequest(BaseModel):
    pertanyaan: str = Field(min_length=3, max_length=500)


class FaqResponse(BaseModel):
    jawaban: str
    sumber: list[str]
    mode: str  # "generative" atau "fallback"
