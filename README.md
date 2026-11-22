# Haoxing AI Service (A26-CS063)

Layanan AI untuk aplikasi Haoxing Mandarin Center: saran level Shuo dari rubrik penilaian laoshi dan asisten FAQ. Disajikan lewat **FastAPI** (Swagger di `/docs`) dan dipanggil oleh back-end aplikasi (Express).

## 1. Masalah yang diselesaikan model
Penempatan level Shuo (1-5) saat ini dinilai laoshi dengan rubrik 6 poin (pre-test dipakai untuk Shuo 3-5; kelas HSK memakai sertifikat). Penilaian yang tidak konsisten membuat level sering tidak sesuai, dan Haoxing tidak memberi refund setelah kelas berjalan. Model memberi **saran level Shuo 1-5** dari 6 skor rubrik. Laoshi tetap memutuskan, dan level final disimpan untuk melatih ulang model. Asisten FAQ menjawab pertanyaan calon siswa (program, harga, jadwal, asrama, refund) dari brosur Haoxing dengan Gemini, dan tetap menjawab dari kutipan brosur bila Gemini gagal (mode fallback).

## 2. Data dan sumber
| Item | Sumber |
|---|---|
| `data/raw/rubrik_shuo_sintetis.csv` (600 baris) | Data **tiruan** dari `src/make_dummy_rubrik.py` (seed 42) mengikuti struktur rubrik. Bukan data siswa asli. Akan diganti data penilaian laoshi (6 skor + level final) dari aplikasi atau dataset tim Data Science |
| Rubrik 6 poin, bobot, kategori nilai | Dokumen "Rubrik Penilaian Kelas Speaking" dari Haoxing Mandarin Center |
| Daftar level (Shuo 1-5, HSK 1-4B), aturan pre-test | Keterangan pihak Haoxing (admin) lewat WhatsApp |
| `data/faq/program_haoxing.md` | Brosur resmi Haoxing dan keterangan pihak Haoxing (pre-test, refund, pembayaran, asrama) |
| `data/raw/students_and_pretest.csv`, `transactions_and_cashbook.csv`, `student_reviews.csv` | Data dummy buatan tim Data Science. Format lama, tidak dipakai pelatihan saat ini (ulasan untuk Side Quest) |
| Library | FastAPI, scikit-learn, pandas, joblib, httpx, python-dotenv (open source) |
| Gemini API | Layanan generative AI (Google), model `gemini-3.5-flash-lite`, kunci lewat variabel lingkungan |

## 3. Preprocessing (`src/preprocess.py`)
1. Buang duplikat `id`, baris dengan nilai kosong, nilai di luar 0-100, dan label di luar Shuo 1-5.
2. Fitur: 6 poin rubrik (`pelafalan`, `kelancaran`, `tata_bahasa`, `kosakata`, `nada`, `komunikasi`), masing-masing 0-100. Nilai akhir (rata-rata berbobot 20/20/20/20/10/10) dan kategori (Excellent sampai Needs Improvement) dihitung di API, bukan fitur model.
3. Target = level Shuo 1-5. Level HSK tidak diprediksi karena ditentukan sertifikat.
4. Pembagian data 80/20 (stratified, seed 42). CV 5-fold pada data latih; model akhir dilatih ulang di seluruh data untuk deployment.

## 4. Perbandingan model
Hasil dari `python -m src.train_level` (otomatis ditulis ke `docs/model_comparison.md`):

| Model | CV F1-macro | Akurasi uji | F1-macro uji |
|---|---|---|---|
| Baseline (kelas mayoritas) | 0.066 | 0.200 | 0.067 |
| Logistic Regression | 0.579 | 0.617 | 0.610 |
| Random Forest | 0.563 | 0.583 | 0.580 |

**Model terpilih: Logistic Regression** (CV F1-macro tertinggi di antara model non-baseline, dan lebih sederhana). Metrik F1-macro dipilih agar setiap level dihitung setara.

**Keterbatasan:** data masih tiruan, dan level yang bersebelahan sengaja dibuat saling tumpang tindih karena rubrik menilai kualitas berbicara, bukan level mutlak. Angka di atas hanya menunjukkan alur pelatihan berjalan, bukan kualitas pada data asli Haoxing. Hasil hanya saran; laoshi memutuskan level. Latih ulang setelah data penilaian laoshi terkumpul.
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