# Sistem Deteksi & Pengenalan Wajah Manusia dengan Deep Learning

Proyek ini punya dua tahap, **keduanya berbasis Convolutional Neural Network (CNN)**,
bukan metode computer vision klasik:

| Tahap | Model | Jenis |
|---|---|---|
| 1. Deteksi lokasi wajah | SSD (Single Shot Detector) + backbone ResNet-10 | Deep Learning (CNN) |
| 2. Ekstraksi fitur wajah | OpenFace `nn4.small2.v1` (arsitektur mirip Inception, dilatih triplet loss — pendekatan sama dengan FaceNet) | Deep Learning (CNN) |
| 3. Klasifikasi identitas | SVM (Support Vector Machine) di atas fitur/embedding hasil CNN | Machine Learning klasik (bukan bagian ekstraksi fitur) |

Kenapa masih ada SVM di tahap akhir? Karena embedding CNN sifatnya **generik**
(bisa merepresentasikan wajah siapa pun, bukan cuma yang ada di dataset kita).
SVM-lah yang mempelajari secara spesifik "vektor seperti apa yang termasuk si A,
dan seperti apa yang termasuk si B" berdasarkan dataset yang kamu siapkan.
**Pipeline CNN-embedding + classifier ringan (SVM) ini adalah arsitektur standar
pada riset face recognition modern** (FaceNet, OpenFace, ArcFace, dsb) — bukan
pendekatan konvensional seperti Eigenface/Fisherface/LBPH yang murni statistik
tanpa neural network.

## Struktur Proyek

```
face_detection_system/
├── models/
│   ├── deploy.prototxt                          # Arsitektur CNN deteksi (SSD ResNet-10)
│   ├── res10_300x300_ssd_iter_140000.caffemodel # Bobot CNN deteksi
│   └── openface_nn4.small2.v1.t7                # Bobot CNN embedding wajah (128-d)
├── src/
│   ├── __init__.py
│   ├── config.py            # Semua pengaturan (path, threshold, warna, dll)
│   ├── model_loader.py      # Memuat model deteksi ke OpenCV DNN
│   ├── preprocessing.py     # Mengubah gambar mentah -> blob input model deteksi
│   ├── detection.py         # Forward pass CNN deteksi + filtering hasil
│   ├── visualization.py     # Menggambar bounding box, label, overlay FPS
│   ├── detector.py          # FaceDetector: penghubung modul deteksi
│   ├── face_utils.py        # Crop wajah hasil deteksi
│   ├── embedder.py          # FaceEmbedder: CNN penghasil embedding 128-d (DEEP LEARNING)
│   ├── dataset_loader.py    # Membaca folder dataset/ -> embedding utk training
│   └── recognizer.py        # FaceRecognizer: SVM classifier di atas embedding
├── dataset/                 # ISI DATASET KAMU DI SINI (lihat panduan di bawah)
│   ├── nama_orang_1/
│   │   ├── foto1.jpg
│   │   └── foto2.jpg
│   └── nama_orang_2/
│       └── foto1.jpg
├── trained_model/           # Model hasil training tersimpan di sini (otomatis)
├── images/                  # Taruh gambar input di sini
├── output/                  # Hasil deteksi/pengenalan tersimpan di sini
├── download_model.py        # Script unduh ketiga model (sudah otomatis dijalankan)
├── detect_image.py          # Deteksi wajah (tanpa identitas) pada 1 file gambar
├── detect_webcam.py         # Deteksi wajah real-time via webcam
├── capture_dataset.py       # Ambil foto dataset otomatis lewat webcam
├── train_recognizer.py      # Latih model pengenalan wajah dari dataset/
├── recognize_image.py       # Deteksi + kenali identitas pada 1 file gambar
├── recognize_webcam.py      # Deteksi + kenali identitas real-time via webcam
├── requirements.txt
└── README.md
```

### Panduan Edit Cepat

| Ingin mengubah...                                | Edit file ini              |
|---------------------------------------------------|-----------------------------|
| Path model, ambang batas default, warna box        | `src/config.py`             |
| Cara model deteksi dimuat                          | `src/model_loader.py`       |
| Cara gambar diproses sebelum masuk model deteksi   | `src/preprocessing.py`      |
| Logika deteksi / cara filter hasil                 | `src/detection.py`          |
| Tampilan kotak, label, teks FPS                    | `src/visualization.py`      |
| Cara model embedding CNN menghasilkan vektor       | `src/embedder.py`           |
| Cara baca folder dataset -> data training           | `src/dataset_loader.py`     |
| Algoritma classifier (SVM) & ambang batas probabilitas | `src/recognizer.py` / `src/config.py` |
| Alur program deteksi gambar / webcam               | `detect_image.py` / `detect_webcam.py` |
| Alur program pengenalan gambar / webcam            | `recognize_image.py` / `recognize_webcam.py` |

## Cara Instalasi

1. Pastikan Python 3.8+ terpasang.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Unduh model (jika folder `models/` kosong):
   ```bash
   python download_model.py
   ```
   Ini akan mengunduh 3 file: model deteksi (prototxt + caffemodel) dan model
   embedding wajah (openface_nn4.small2.v1.t7).

## Cara Penggunaan — Deteksi Saja (Tanpa Identitas)

```bash
python detect_image.py --image images/nama_file.jpg
python detect_webcam.py
```
Tekan `q` untuk keluar dari jendela webcam.

## Cara Penggunaan — Deteksi + Pengenalan Identitas (Dataset)

### Langkah 1 — Siapkan Dataset

Buat folder untuk setiap orang yang ingin dikenali di dalam `dataset/`, lalu isi
dengan foto wajah orang tersebut (disarankan **15-30 foto per orang**, dari sudut
dan ekspresi yang bervariasi, agar model lebih akurat):

```
dataset/
├── budi/
│   ├── budi_001.jpg
│   ├── budi_002.jpg
│   └── ...
└── siti/
    ├── siti_001.jpg
    └── ...
```

**Opsi A — Ambil otomatis lewat webcam (paling praktis):**
```bash
python capture_dataset.py --name budi --jumlah 30
```
Tekan `SPASI` untuk mulai merekam wajah secara otomatis, `q` untuk berhenti.
Ulangi untuk setiap orang (`--name siti`, dst).

**Opsi B — Kumpulkan foto secara manual**, lalu taruh langsung ke folder
`dataset/<nama_orang>/`. Bisa juga memakai dataset publik seperti
[Labeled Faces in the Wild (LFW)](http://vis-www.cs.umass.edu/lfw/) sebagai sumber
foto tambahan/pembanding jika dosen meminta dataset dari sumber akademik.

### Langkah 2 — Latih Model

```bash
python train_recognizer.py
```
Script ini akan: membaca semua foto di `dataset/`, mendeteksi wajah tiap foto
(CNN SSD ResNet-10), mengekstrak embedding 128-d-nya (CNN OpenFace), lalu
melatih SVM classifier dari seluruh embedding tersebut. Hasil tersimpan di
`trained_model/`.

Jalankan ulang setiap kali dataset berubah (nambah orang / nambah foto).

### Langkah 3 — Jalankan Pengenalan

```bash
# Pada gambar
python recognize_image.py --image images/foto_test.jpg

# Real-time via webcam
python recognize_webcam.py
```

Kotak **hijau** = wajah dikenali (beserta nama & persentase keyakinan).
Kotak **merah** = wajah terdeteksi tapi keyakinan classifier di bawah ambang batas
("Tidak Dikenal"). Ambang batas ini bisa diubah di `src/config.py`
(`RECOGNITION_PROBABILITY_THRESHOLD` — semakin tinggi nilainya, semakin ketat).

## Cara Kerja Sistem (Ringkasan Teknis)

### Tahap 1 — Deteksi Wajah (CNN, SSD ResNet-10)

1. **Preprocessing** — Gambar diubah ukurannya menjadi 300×300 piksel dan
   dinormalisasi (mean subtraction).
2. **Forward Pass CNN** — Gambar diproses melalui jaringan SSD ResNet-10 yang
   telah dilatih pada dataset wajah skala besar, menghasilkan ratusan kandidat
   kotak deteksi beserta skor kepercayaan.
3. **Filtering** — Kandidat dengan confidence di bawah ambang batas (default 0.5)
   dibuang.
4. **Post-processing** — Koordinat kotak dikembalikan ke skala gambar asli.

### Tahap 2 — Ekstraksi Fitur / Embedding (CNN, OpenFace)

1. Area wajah hasil deteksi dipotong (crop), diresize ke 96×96 piksel.
2. Gambar dilewatkan melalui jaringan CNN (arsitektur mirip Inception) yang
   sudah dilatih dengan **triplet loss** menggunakan jutaan pasangan wajah.
3. Output-nya adalah **vektor 128 dimensi** yang merepresentasikan "sidik jari
   wajah" tersebut. Sifat kuncinya: dua foto dari orang yang sama akan
   menghasilkan vektor yang jaraknya (Euclidean distance) berdekatan, sedangkan
   foto dari orang berbeda akan menghasilkan vektor yang berjauhan — properti
   ini didapat murni dari pembelajaran CNN, bukan dihitung dengan rumus statistik
   tetap seperti pada metode klasik.

### Tahap 3 — Klasifikasi Identitas (SVM)

1. Saat training, seluruh vektor embedding dari dataset + label namanya dipakai
   untuk melatih **SVM (Support Vector Machine)** berkernel linear, yang belajar
   memisahkan "wilayah" vektor milik tiap orang di ruang 128 dimensi.
2. Saat pengenalan, wajah baru diubah jadi embedding dengan cara yang sama,
   lalu SVM memprediksi probabilitas wajah tersebut milik masing-masing orang
   di dataset.
3. Jika probabilitas tertinggi berada di atas ambang batas, wajah dianggap
   "dikenali" dengan nama tersebut; jika di bawah, dianggap "Tidak Dikenal".

## Kemungkinan Pengembangan Lanjutan

- **Akurasi lebih tinggi**: ganti model embedding dengan FaceNet (Inception ResNet v1,
  dilatih di VGGFace2) atau ArcFace, yang punya akurasi lebih tinggi pada benchmark LFW.
- **Deteksi Landmark Wajah**: tambahkan model landmark (mata, hidung, mulut) untuk
  alignment wajah sebelum embedding, biasanya meningkatkan akurasi recognition.
- **Deploy sebagai API**: bungkus pipeline ini dengan FastAPI/Flask agar bisa
  dipanggil dari aplikasi web/mobile.
- **Model deteksi lebih modern**: ganti SSD ResNet-10 dengan MTCNN, RetinaFace,
  atau YOLO-Face untuk akurasi lebih tinggi pada kondisi ekstrem (wajah sangat
  kecil, sangat gelap, dsb).

## Catatan untuk Laporan/Tugas

- Seluruh tahap ekstraksi fitur (deteksi maupun embedding wajah) memakai
  **jaringan neural konvolusional (CNN) pretrained**, bukan fitur tangan
  (hand-crafted features) seperti Haar Cascade, HOG, LBPH, atau Eigenface.
- SVM di tahap akhir **bukan** bagian dari ekstraksi fitur — ia hanya lapisan
  klasifikasi tipis di atas fitur yang sudah dipelajari CNN. Ini adalah desain
  yang umum dipakai di banyak paper face recognition (embedding CNN + classifier
  ringan), berbeda dengan pipeline "konvensional" yang sepenuhnya tanpa neural
  network.
- Referensi konsep: *FaceNet: A Unified Embedding for Face Recognition and
  Clustering* (Schroff et al., 2015) — dasar pendekatan embedding wajah yang
  dipakai OpenFace pada proyek ini.
"# FACE-DETECTION" 
