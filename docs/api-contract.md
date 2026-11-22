# Kontrak API AI Service (draf, sepakati dengan FS-2 di minggu 1)

Base URL: `https://haoxing-ai-service.fastapicloud.dev`. Swagger: `/docs`. Backend: simpan di `AI_SERVICE_URL`, dan pakai timeout 35 detik untuk `/api/v1/faq` (paket gratis bisa tidur saat idle, jadi panggilan pertama dapat lebih lambat).

## GET /health
200: `{"status":"ok","model_loaded":true}`

## POST /api/v1/predict-level
Saran level Shuo dari 6 poin rubrik penilaian laoshi (tiap poin 0-100). Hanya saran, keputusan akhir di laoshi.
Request:
```json
{"pelafalan": 80, "kelancaran": 75, "tata_bahasa": 70, "kosakata": 65, "nada": 70, "komunikasi": 60}
```
Bobot nilai akhir: pelafalan, kelancaran, tata_bahasa, kosakata masing-masing 20%; nada dan komunikasi masing-masing 10%.
Response 200:
```json
{"level_saran": "Shuo 3", "probabilitas": {"Shuo 1": 0.0, "Shuo 2": 0.1, "Shuo 3": 0.7, "Shuo 4": 0.2, "Shuo 5": 0.0}, "nilai_akhir": 71.0, "kategori": "Good", "catatan": "Saran saja, keputusan akhir di laoshi", "model": "Logistic Regression"}
```
Level: Shuo 1 sampai Shuo 5. Kategori: 90-100 Excellent, 80-89 Very Good, 70-79 Good, 60-69 Fair, di bawah 60 Needs Improvement.
Kode error: 422 (poin di luar 0-100, hilang, atau bukan angka), 503 (model belum tersedia).
Catatan: model awal dilatih data tiruan, jadi anggap saran awal. Backend menyimpan skor, level_saran, dan level_final dari laoshi untuk melatih ulang model.
## POST /api/v1/faq
Request: `{"pertanyaan": "Berapa harga HSK 2?"}`
Response 200: `{"jawaban": "...", "sumber": ["..."], "mode": "generative" | "fallback"}`
Kode error: 422 (pertanyaan kosong atau lebih dari 500 karakter).
Catatan: jika layanan generative AI gagal atau kuota habis, `mode` = `fallback` dan jawaban tetap berisi kutipan data program. Pertanyaan di luar topik dijawab sopan bahwa informasi tidak tersedia.

## Catatan integrasi untuk backend
- Backend yang memanggil layanan ini; frontend tidak memanggil langsung.
- Jika `/predict-level` gagal atau timeout, backend menampilkan pesan jelas dan level diisi manual admin.
- Layanan gratis bisa tidur saat idle: set timeout 30-60 detik dan coba ulang sekali.
