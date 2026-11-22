# Haoxing AI Service (A26-CS063)

Layanan AI untuk aplikasi Haoxing Mandarin Center: rekomendasi tingkat kelas dari skor pre-test dan asisten FAQ. Disajikan lewat **FastAPI** (Swagger di `/docs`) dan dipanggil oleh back-end aplikasi (Express).

## 1. Masalah yang diselesaikan model
Admin menentukan level siswa secara manual dari hasil pre-test sehingga level sering tidak sesuai dan memicu permintaan refund (kebijakan lembaga: tanpa refund). Model memberi **rekomendasi tingkat** (Basic, Tingkat 1-4) dari tiga skor pre-test; admin tetap dapat mengubahnya. Asisten FAQ membantu admin menjawab pertanyaan calon siswa (program, harga, jadwal) agar tidak berulang.

## 2. Data dan sumber
| Item | Sumber |
|---|---|
| `data/raw/students_and_pretest.csv` (120 siswa) | Data dummy buatan tim Data Science (bukan data asli siswa) |
| `data/raw/transactions_and_cashbook.csv`, `student_reviews.csv` | Data dummy buatan tim Data Science (dipakai FS/DS; ulasan untuk Side Quest) |
| `data/faq/program_haoxing.md` | Brosur resmi Haoxing (diterima 20 Nov 2026) dan keterangan pihak Haoxing |
| Library | FastAPI, scikit-learn, pandas, joblib, httpx (open source) |
| Gemini API | Layanan generative AI (Google), kunci lewat `.env` |

## 3. Preprocessing (`src/preprocess.py`)
1. Hapus duplikat `student_id`, buang baris dengan skor kosong atau di luar 0-100.
2. Fitur: `skor_pretest`, `skor_listening`, `skor_grammar`.
3. **Target = tingkat saja** (Basic, Tingkat 1-4), bukan label jalur. Alasan: pada data dummy, rentang skor sama untuk jalur HSK, Grammar, dan Shuo, jadi jalur tidak dapat diprediksi dari skor. Jalur dipilih admin.
4. Pembagian data 80/20 (stratified, seed 42). CV 5-fold pada data latih; model akhir dilatih ulang di seluruh data untuk deployment.

## 4. Perbandingan model
Hasil dari `python -m src.train_level` (otomatis ditulis ke `docs/model_comparison.md`):

| Model | CV F1-macro | Akurasi uji | F1-macro uji |
|---|---|---|---|
| Baseline (kelas mayoritas) | 0.08 | 0.25 | 0.08 |
| Logistic Regression | 0.803 | 0.833 | 0.817 |
| Random Forest | 0.952 | 0.958 | 0.964 |

**Model terpilih: Random Forest** (CV F1-macro tertinggi). Metrik dipilih F1-macro karena jumlah siswa per tingkat tidak sama.

**Keterbatasan:** data dummy kecil (120 baris) dan label tampaknya mengikuti rentang skor, sehingga skor tinggi belum tentu berlaku pada data asli Haoxing. Rekomendasi hanya saran; admin dapat mengubah level.

## 5. Menjalankan
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # isi GEMINI_API_KEY (opsional; tanpa kunci jawaban FAQ mode fallback)
python -m src.train_level       # melatih dan menyimpan models/level_model.joblib
uvicorn src.app.main:app --reload   # http://127.0.0.1:8000/docs
pytest -q                       # uji
```

## 6. Deploy (gratis)
Hosting: FastAPI Cloud (paket Hobby, tanpa kartu). `requirements.txt` memakai `fastapi[standard]`, dan `main.py` di folder root menjadi pintu masuk aplikasi.

1. `pip install "fastapi[standard]"`
2. `fastapi login` (sekali saja, lewat browser)
3. `fastapi deploy` dari folder repo. Deploy pertama menanyakan tim dan nama aplikasi (`haoxing-ai-service`).
4. Di dashboard FastAPI Cloud, menu Configuration, isi `GEMINI_API_KEY` (rahasia, jangan di repositori) dan `GEMINI_MODEL=gemini-3.5-flash-lite`.

Deploy memakai isi folder lokal, jadi jalankan `git pull` di `main` dulu dan pastikan tidak ada perubahan yang belum di-merge.
## 7. Kontrak API
Lihat `docs/api-contract.md`.

## 8. Struktur
```
src/preprocess.py   preprocessing dan pemetaan target
src/train_level.py  latih + bandingkan model
src/app/            FastAPI (main, schemas, faq)
tests/              uji API
models/             model terlatih
docs/               kontrak API, perbandingan model
```



## Deploy publik
Base URL: https://haoxing-ai-service.fastapicloud.dev
- Swagger di `/docs`, cek hidup di `/health`.
- Paket gratis bisa tidur saat lama tidak dipakai, jadi panggilan pertama setelah idle dapat lebih lambat. Backend sebaiknya memakai timeout 35 detik untuk `/api/v1/faq`.
- `/api/v1/predict-level` masih draf. Kontrak lengkap di `docs/api-contract.md`.