# 🛒 Commerce App

Backend REST API untuk platform e-commerce berbasis Django & Django REST Framework. Dibangun dengan arsitektur modular, autentikasi JWT, dan sistem role-based access control (RBAC).

---

## 🚀 Tech Stack

| Kategori | Teknologi |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | Django 5.x, Django REST Framework |
| **Database** | PostgreSQL |
| **Auth** | Simple JWT, OAuth2 (Google & Facebook) |
| **Task Queue** | Celery |
| **Message Broker** | Redis |
| **Email** | Gmail SMTP |
| **API Docs** | drf-spectacular (Swagger & ReDoc) |
| **Token** | itsdangerous (email verification) |

---

## 📁 Struktur Project

```
commerce/
├── config/              # Konfigurasi utama (settings, urls, celery)
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── users/               # Auth, profile, manajemen akun
├── sellers/             # Permohonan seller
├── admin_panel/         # Review permohonan (khusus admin)
└── utils/               # Helper (response wrapper, dll)
```

---

## ✅ Fitur yang Sudah Selesai

### 🔐 Authentication
- [x] Register dengan validasi password kuat
- [x] Login dengan JWT (Access & Refresh Token)
- [x] Logout dengan blacklist refresh token
- [x] Social Login — Google & Facebook
- [x] Link & Unlink social account

### 📧 Email Verification
- [x] Kirim email verifikasi saat register (async via Celery)
- [x] Verifikasi token via link email
- [x] Resend email verifikasi

### 🔑 Password Management
- [x] Forgot Password — kirim link reset via email
- [x] Reset Password — validasi token & update password
- [x] Change Password — untuk user yang sudah login
- [x] Blacklist semua session lama setelah ganti password

### 👤 Profile
- [x] Update profil (nama, foto, alamat, nomor HP)
- [x] Delete akun dengan konfirmasi password

### 🏪 Seller Application
- [x] Buyer ajukan permohonan menjadi seller
- [x] Cek status permohonan
- [x] Batalkan permohonan (jika masih pending)
- [x] History permohonan (termasuk yang ditolak)

### 🛡️ Admin Panel
- [x] Lihat semua permohonan (filter by status)
- [x] Approve permohonan → role buyer otomatis jadi seller
- [x] Reject permohonan → notifikasi email dengan alasan penolakan

---

## 🔲 Fitur yang Akan Datang

### 🏪 Toko (Seller)
- [ ] Buat & kelola toko
- [ ] Upload produk
- [ ] Manajemen stok

### 🛍️ Transaksi (Buyer)
- [ ] Keranjang belanja
- [ ] Checkout & pembayaran
- [ ] Riwayat transaksi

### ⭐ Review & Rating
- [ ] Review produk
- [ ] Rating seller

### 📊 Dashboard
- [ ] Dashboard seller (statistik penjualan)
- [ ] Dashboard admin (statistik platform)

---


## ⚙️ Setup & Instalasi

### 1. Clone & Virtual Environment
```bash
git clone https://github.com/username/commerce.git
cd commerce
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Buat file `.env` di root project:
```env
# Database
DB_NAME=commerce
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Social Auth
GOOGLE_CLIENT_ID=your-google-client-id
FACEBOOK_CLIENT_ID=your-facebook-client-id

# Email
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

```

### 4. Migrasi Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Buat Admin
```bash
python manage.py create_admin --email=admin@gmail.com --password=Admin123! --firstname=Admin
```

### 6. Jalankan Server
```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Celery Worker
celery -A config worker --loglevel=info --pool=solo

# Terminal 3 — Redis (via Docker)
docker run -d -p 6379:6379 redis:alpine
```

### 7. API Documentation
```
Swagger : http://localhost:8000/api/docs/
ReDoc   : http://localhost:8000/api/redoc/
```

---

## 👤 Role System

| Role | Akses |
|---|---|
| `buyer` | Belanja, ajukan permohonan seller |
| `seller` | Semua akses buyer + kelola toko & produk |
| `admin` | Semua akses + review permohonan & manajemen platform |

---

