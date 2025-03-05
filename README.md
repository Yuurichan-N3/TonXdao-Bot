# TONxDAO Automation Tool

## Deskripsi
TONxDAO Automation Tool adalah alat otomatisasi berbasis Python yang dirancang untuk mengelola tugas harian di platform TONxDAO, seperti check-in, farming, dan tugas otomatis lainnya. Alat ini memungkinkan pengguna untuk memantau status akun mereka melalui tabel interaktif di terminal, dengan fitur seperti pembaruan real-time dan dukungan untuk beberapa akun secara paralel.

Proyek ini dikembangkan oleh [sentineldiscus](https://t.me/sentineldiscus) dan dirancang untuk mempermudah pengguna dalam mengotomatiskan aktivitas di TONxDAO.

## Fitur
- **Auto Check-in Harian**: Melakukan check-in otomatis untuk setiap akun.
- **Auto Farming**: Mengelola energi dan koin melalui proses farming otomatis.
- **Support Multi-Account**: Menangani beberapa akun secara bersamaan menggunakan file `data.txt`.
- **Tabel Status Interaktif**: Menampilkan status akun (Token Status, Check-in, Username, Farm, Coins, Energy) dalam format tabel yang terformat di terminal.
- **Pembaruan Real-time**: Memperbarui status setiap 10 detik untuk memantau aktivitas akun secara langsung.

## Prasyarat
Pastikan Anda memiliki lingkungan berikut sebelum menjalankan alat ini:
- **Python 3.8+**
- **Dependensi Python**: Instal dependensi berikut menggunakan `pip`:
  ```bash
  pip install requests websocket-client tabulate termcolor
  ```


## Instalasi
1. Cloning Repository:

```
git clone https://github.com/Yuurichan-N3/TonXdao-Bot.git
cd TonXdao-Bot
```

2. Siapkan File Data:
Buat file `data.txt` di direktori proyek dengan format satu query per baris (contoh: initData untuk login ke TONxDAO).

Contoh isi `data.txt:`

```
query_id=
query_id=
```


Jalankan Skrip:

```
python bot.py
```



## 📜 Lisensi  

Script ini didistribusikan untuk keperluan pembelajaran dan pengujian. Penggunaan di luar tanggung jawab pengembang.  

Untuk update terbaru, bergabunglah di grup **Telegram**: [Klik di sini](https://t.me/sentineldiscus).


---

## 💡 Disclaimer
Penggunaan bot ini sepenuhnya tanggung jawab pengguna. Kami tidak bertanggung jawab atas penyalahgunaan skrip ini.
