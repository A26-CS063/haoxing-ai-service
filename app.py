"""Entry point untuk Hugging Face Spaces (SDK Gradio, tanpa UI Gradio).

Menjalankan aplikasi FastAPI apa adanya di port 7860.
"""
import os

import uvicorn

from src.app.main import app  # noqa: F401  (dipakai uvicorn)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
