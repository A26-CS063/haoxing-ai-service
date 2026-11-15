# Kontrak API AI Service (draf, sepakati dengan FS-2 di minggu 1)

Base URL: `https://<service>.onrender.com` (ganti setelah deploy). Swagger: `/docs`.

## GET /health
200: `{"status":"ok","model_loaded":true}`

## POST /api/v1/predict-level
Request:
```json
{"skor_pretest": 72, "skor_listening": 65, "skor_grammar": 78}
```
Response 200:
```json
{"tingkat": "Tingkat 2", "probabilitas": {"Basic": 0.0, "Tingkat 1": 0.05, "Tingkat 2": 0.9, "Tingkat 3": 0.05, "Tingkat 4": 0.0}, "model": "Random Forest"}
```
Kode error: 422 (skor di luar 0-100 / field hilang / bukan angka), 503 (model belum tersedia).

## POST /api/v1/faq
Request: `{"pertanyaan": "Berapa harga HSK 2?"}`
Response 200: `{"jawaban": "...", "sumber": ["..."], "mode": "generative" | "fallback"}`
Kode error: 422 (pertanyaan kosong atau lebih dari 500 karakter).
Catatan: jika layanan generative AI gagal atau kuota habis, `mode` = `fallback` dan jawaban tetap berisi kutipan data program. Pertanyaan di luar topik dijawab sopan bahwa informasi tidak tersedia.

## Catatan integrasi untuk backend
- Backend yang memanggil layanan ini; frontend tidak memanggil langsung.
- Jika `/predict-level` gagal atau timeout, backend menampilkan pesan jelas dan level diisi manual admin.
- Layanan gratis bisa tidur saat idle: set timeout 30-60 detik dan coba ulang sekali.
