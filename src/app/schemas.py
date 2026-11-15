from pydantic import BaseModel, Field


class PredictLevelRequest(BaseModel):
    skor_pretest: float = Field(ge=0, le=100)
    skor_listening: float = Field(ge=0, le=100)
    skor_grammar: float = Field(ge=0, le=100)


class PredictLevelResponse(BaseModel):
    tingkat: str
    probabilitas: dict[str, float]
    model: str


class FaqRequest(BaseModel):
    pertanyaan: str = Field(min_length=3, max_length=500)


class FaqResponse(BaseModel):
    jawaban: str
    sumber: list[str]
    mode: str  # "generative" atau "fallback"
