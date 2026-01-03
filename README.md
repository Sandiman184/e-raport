# Sistem Informasi Raport Digital (E-Raport) - Al Barokah

Aplikasi berbasis web untuk manajemen penilaian, data santri, dan pelaporan hasil belajar (raport) di Madrasah Diniyah Takmiliyah Al Barokah. Aplikasi ini dirancang untuk mempermudah administrasi akademik dengan antarmuka yang modern dan responsif.

## 📋 Fitur Utama

*   **Dashboard Statistik**: Ringkasan data santri, kelas, dan status sistem.
*   **Manajemen Data Santri**: Tambah, ubah, hapus, dan pencarian data santri.
*   **Input Nilai Akademik**: Pengisian nilai per mata pelajaran dan semester.
*   **Input Ekstrakurikuler**: Pencatatan kehadiran, kedisiplinan, dan catatan wali kelas.
*   **Cetak Raport**: Generasi raport otomatis siap cetak.
*   **Manajemen Database**:
    *   Backup & Restore data (mendukung backup per tahun ajar).
    *   Fitur "Zone Bahaya" untuk penghapusan data tahunan (Prune) atau reset total.
    *   Estimasi ukuran backup real-time.
*   **Pengaturan Sekolah**: Kustomisasi identitas madrasah, kepala sekolah, dan tahun ajaran.

## 🛠️ Persyaratan Sistem

*   **Python**: Versi 3.10 atau lebih baru.
*   **Sistem Operasi**: Windows, macOS, atau Linux.
*   **Browser**: Google Chrome, Mozilla Firefox, atau Microsoft Edge (terbaru).

## 🚀 Panduan Instalasi

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di lingkungan lokal:

### 1. Clone Repository (atau Ekstrak File)
Pastikan Anda berada di direktori proyek:
```bash
cd "d:\Project\Albarokah\Raport fix\web_app"
```

### 2. Buat Virtual Environment
Disarankan menggunakan virtual environment agar dependensi tidak tercampur.

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instal Dependensi
Install pustaka Python yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Awal (Opsional)
Aplikasi menggunakan `config.py` untuk pengaturan dasar. Secara default, aplikasi menggunakan database SQLite lokal di folder `storage/`.

## 🖥️ Cara Menjalankan Aplikasi

Jalankan perintah berikut untuk memulai server lokal:

```bash
python run.py
```

Setelah server berjalan, buka browser dan akses alamat berikut:
**http://localhost:5005**

### Akun Default
Jika database masih kosong, Anda mungkin perlu membuat akun admin pertama kali melalui shell flask atau database seeder (jika tersedia), atau hubungi administrator sistem.

*Catatan: Secara default aplikasi berjalan dalam mode DEBUG. Untuk produksi, pastikan setting `FLASK_DEBUG=0`.*

## 📚 Struktur Proyek

```
web_app/
├── app/
│   ├── core/           # Ekstensi inti (Database, Login Manager)
│   ├── models/         # Model Database (User, Student, Grade, dll)
│   ├── modules/        # Modul/Blueprint (Dashboard, Auth, Students, dll)
│   └── services/       # Layanan Logika Bisnis (Backup, Import)
├── storage/            # Tempat penyimpanan Database & Backup
├── web/
│   ├── static/         # Aset statis (CSS, JS, Gambar)
│   └── templates/      # File HTML (Jinja2)
├── config.py           # Konfigurasi Aplikasi
├── requirements.txt    # Daftar Dependensi
└── run.py              # Entry point aplikasi
```

## 🤝 Kontribusi

Jika Anda ingin berkontribusi pada pengembangan proyek ini:
1.  Fork repository ini.
2.  Buat branch fitur baru (`git checkout -b fitur-baru`).
3.  Commit perubahan Anda (`git commit -m 'Menambah fitur X'`).
4.  Push ke branch (`git push origin fitur-baru`).
5.  Buat Pull Request.

## 📄 Lisensi

Hak Cipta © 2024 - Madrasah Diniyah Takmiliyah Al Barokah.
Seluruh hak cipta dilindungi undang-undang. Penggunaan internal.
