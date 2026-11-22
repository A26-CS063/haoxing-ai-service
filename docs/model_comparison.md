| Model | CV F1-macro (5-fold, data latih) | Akurasi (data uji) | F1-macro (data uji) |
|---|---|---|---|
| Baseline (kelas mayoritas) | 0.066 | 0.2 | 0.067 |
| Logistic Regression | 0.579 | 0.617 | 0.61 |
| Random Forest | 0.563 | 0.583 | 0.58 |

Model terpilih: **Logistic Regression** (CV F1-macro tertinggi di antara model non-baseline).

Catatan: model ini dilatih dengan data TIRUAN (`data/raw/rubrik_shuo_sintetis.csv`), jadi angka di atas
hanya menunjukkan alur berjalan, bukan kualitas di data nyata. Latih ulang setelah data penilaian laoshi terkumpul.
