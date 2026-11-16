"""
sample_data.py
Modul untuk membangkitkan data dummy realistis (15-20 item)
sesuai skenario presentasi di PDF (Ahmad & Budi, Charger, Botol, Jaket, dll).
"""

from typing import List, Dict, Any


def get_initial_lost_items() -> List[Dict[str, Any]]:
    return [
        {
            "id": "LOST-2026-001",
            "name": "Charger Laptop Asus",
            "category": "Elektronik",
            "color": "Hitam",
            "description": "Charger laptop Asus 65W, ujung kabel ada sedikit lakban bening, ada stiker kucing kecil",
            "location": {
                "floor": 2,
                "room_code": "LAB201",
                "room_name": "Lab Komputer 201"
            },
            "date": "2026-11-14",
            "time": "10:30",
            "status": "Dilaporkan",
            "reporter": "Ahmad Rizky"
        },
        {
            "id": "LOST-2026-002",
            "name": "Jaket Hoodie Hitam",
            "category": "Pakaian / Aksesoris",
            "color": "Hitam",
            "description": "Hoodie warna hitam polos merk Erigo ukuran XL, ada saku depan",
            "location": {
                "floor": 2,
                "room_code": "LAB202",
                "room_name": "Lab Data 202"
            },
            "date": "2026-11-15",
            "time": "14:15",
            "status": "Dilaporkan",
            "reporter": "Dimas Pratama"
        },
        {
            "id": "LOST-2026-003",
            "name": "Earphone TWS Robot",
            "category": "Elektronik",
            "color": "Putih",
            "description": "Earphone bluetooth case putih ada gantungan karet karakter beruang",
            "location": {
                "floor": 1,
                "room_code": "R101",
                "room_name": "Ruang Kuliah 101"
            },
            "date": "2026-11-14",
            "time": "11:45",
            "status": "Dilaporkan",
            "reporter": "Siti Nurhaliza"
        },
        {
            "id": "LOST-2026-004",
            "name": "Botol Minum Corkcicle",
            "category": "Botol / Tumbler",
            "color": "Biru",
            "description": "Tumbler warna biru navy ukuran 750ml, ada sedikit goresan di dasar botol",
            "location": {
                "floor": 1,
                "room_code": "LOBBY",
                "room_name": "Lobby / Hall"
            },
            "date": "2026-11-15",
            "time": "09:00",
            "status": "Dicocokkan",
            "reporter": "Fajar Hidayat"
        },
        {
            "id": "LOST-2026-005",
            "name": "Tempat Pensil Faber-Castell",
            "category": "Alat Tulis",
            "color": "Abu-abu",
            "description": "Kotak pensil resleting abu-abu isi pulpen sarasa hitam 3 biji dan penggaris 15cm",
            "location": {
                "floor": 1,
                "room_code": "R102",
                "room_name": "Ruang Kuliah 102"
            },
            "date": "2026-11-13",
            "time": "13:00",
            "status": "Selesai",
            "reporter": "Dewi Sartika"
        },
        {
            "id": "LOST-2026-006",
            "name": "Dompet Kulit Cokelat",
            "category": "Tas / Dompet",
            "color": "Cokelat",
            "description": "Dompet pria kulit warna cokelat tua, berisi kartu tanda mahasiswa Sains Data dan e-toll",
            "location": {
                "floor": 1,
                "room_code": "TERAS",
                "room_name": "Area Parkir / Teras Depan"
            },
            "date": "2026-11-12",
            "time": "16:40",
            "status": "Selesai",
            "reporter": "Bagus Wicaksono"
        },
        {
            "id": "LOST-2026-007",
            "name": "Mouse Wireless Logitech",
            "category": "Elektronik",
            "color": "Hitam",
            "description": "Mouse tanpa kabel Logitech M185 warna hitam abu-abu dengan USB dongle menempel",
            "location": {
                "floor": 2,
                "room_code": "LAB201",
                "room_name": "Lab Komputer 201"
            },
            "date": "2026-11-16",
            "time": "11:20",
            "status": "Dilaporkan",
            "reporter": "Muhammad Ilham"
        },
        {
            "id": "LOST-2026-008",
            "name": "Kacamata Frame Bulat",
            "category": "Pakaian / Aksesoris",
            "color": "Hitam",
            "description": "Kacamata minus lensa silinder frame bulat titanium hitam, case merah",
            "location": {
                "floor": 2,
                "room_code": "MUSHOLLA",
                "room_name": "Musholla / Ruang Mahasiswa"
            },
            "date": "2026-11-16",
            "time": "12:45",
            "status": "Dilaporkan",
            "reporter": "Zahra Aulia"
        },
        {
            "id": "LOST-2026-009",
            "name": "Buku Catatan Statistika",
            "category": "Alat Tulis",
            "color": "Biru",
            "description": "Buku tulis spiral Campus warna cover biru, sampul depan tertulis 'Catatan Pemrograman Dasar & Statistika'",
            "location": {
                "floor": 2,
                "room_code": "SEMINAR",
                "room_name": "Ruang Seminar"
            },
            "date": "2026-11-11",
            "time": "15:10",
            "status": "Selesai",
            "reporter": "Nadia Putri"
        },
        {
            "id": "LOST-2026-010",
            "name": "Kabel Data Type-C Fast Charging",
            "category": "Elektronik",
            "color": "Merah",
            "description": "Kabel charger type C braided warna merah panjang 1 meter merk Baseus",
            "location": {
                "floor": 1,
                "room_code": "TU",
                "room_name": "TU / Admin"
            },
            "date": "2026-11-15",
            "time": "10:00",
            "status": "Diklaim",
            "reporter": "Rian Kusuma"
        }
    ]


def get_initial_found_items() -> List[Dict[str, Any]]:
    return [
        {
            "id": "FOUND-2026-001",
            "name": "Charger Laptop Hitam",
            "category": "Elektronik",
            "color": "Hitam",
            "description": "Ditemukan adapter charger laptop Asus 65W tertinggal di colokan bawah meja lab",
            "location": {
                "floor": 2,
                "room_code": "LAB201",
                "room_name": "Lab Komputer 201"
            },
            "date": "2026-11-14",
            "time": "12:15",
            "status": "Dilaporkan",
            "reporter": "Budi Santoso",
            "kept_at": "Dititipkan ke TU"
        },
        {
            "id": "FOUND-2026-002",
            "name": "Tumbler Minum Biru",
            "category": "Botol / Tumbler",
            "color": "Biru",
            "description": "Botol minum stainless steel warna biru gelap tertinggal di kursi tunggu",
            "location": {
                "floor": 1,
                "room_code": "LOBBY",
                "room_name": "Lobby / Hall"
            },
            "date": "2026-11-15",
            "time": "10:30",
            "status": "Dicocokkan",
            "reporter": "Pak Supri (Security)",
            "kept_at": "Dititipkan ke TU"
        },
        {
            "id": "FOUND-2026-003",
            "name": "Flashdisk Sandisk Putih 32GB",
            "category": "Elektronik",
            "color": "Putih",
            "description": "Flashdisk Sandisk Cruzer Blade putih merah tertinggal di wastafel toilet",
            "location": {
                "floor": 1,
                "room_code": "TOILET_L1",
                "room_name": "Toilet L1"
            },
            "date": "2026-11-15",
            "time": "15:20",
            "status": "Dilaporkan",
            "reporter": "Ani Yuliana",
            "kept_at": "Dibawa pelapor"
        },
        {
            "id": "FOUND-2026-004",
            "name": "Tempat Pensil Kain Abu-abu",
            "category": "Alat Tulis",
            "color": "Abu-abu",
            "description": "Kotak pensil kain abu-abu merk Faber-Castell tertinggal di meja depan dosen",
            "location": {
                "floor": 1,
                "room_code": "R102",
                "room_name": "Ruang Kuliah 102"
            },
            "date": "2026-11-13",
            "time": "14:00",
            "status": "Selesai",
            "reporter": "Ibu Ratna (Dosen)",
            "kept_at": "Dititipkan ke TU"
        },
        {
            "id": "FOUND-2026-005",
            "name": "Dompet Cokelat Merk Cardinal",
            "category": "Tas / Dompet",
            "color": "Cokelat",
            "description": "Dompet cokelat ditemukan dekat tangga parkir motor, ada tanda pengenal mahasiswa",
            "location": {
                "floor": 1,
                "room_code": "TERAS",
                "room_name": "Area Parkir / Teras Depan"
            },
            "date": "2026-11-12",
            "time": "17:15",
            "status": "Selesai",
            "reporter": "Pak Supri (Security)",
            "kept_at": "Dititipkan ke TU"
        },
        {
            "id": "FOUND-2026-006",
            "name": "Kabel Charger Merah Type-C",
            "category": "Elektronik",
            "color": "Merah",
            "description": "Kabel charger merah tergeletak di meja front office TU",
            "location": {
                "floor": 1,
                "room_code": "TU",
                "room_name": "TU / Admin"
            },
            "date": "2026-11-15",
            "time": "10:45",
            "status": "Diklaim",
            "reporter": "Mbak Rini (Staf TU)",
            "kept_at": "Dititipkan ke TU"
        },
        {
            "id": "FOUND-2026-007",
            "name": "Kunci Motor Honda dengan Gantungan Akrilik",
            "category": "Pakaian / Aksesoris",
            "color": "Hitam",
            "description": "Kunci kontak motor ada gantungan bertuliskan Sains Data 2025",
            "location": {
                "floor": 1,
                "room_code": "TANGGA_L1",
                "room_name": "Tangga"
            },
            "date": "2026-11-16",
            "time": "08:15",
            "status": "Dilaporkan",
            "reporter": "Bambang Wijaya",
            "kept_at": "Dititipkan ke TU"
        },
        {
            "id": "FOUND-2026-008",
            "name": "Kalkulator Ilmiah Casio fx-991EX",
            "category": "Elektronik",
            "color": "Hitam",
            "description": "Kalkulator scientific Casio hitam putih kondisi normal di laci meja kelas",
            "location": {
                "floor": 2,
                "room_code": "R203",
                "room_name": "Ruang Kuliah 203"
            },
            "date": "2026-11-16",
            "time": "13:30",
            "status": "Dilaporkan",
            "reporter": "Dina Rahma",
            "kept_at": "Ditaruh di lokasi"
        },
        {
            "id": "FOUND-2026-009",
            "name": "Buku Binder Biru",
            "category": "Alat Tulis",
            "color": "Biru",
            "description": "Buku catatan materi kuliah sains data warna biru ditemukan di meja seminar",
            "location": {
                "floor": 2,
                "room_code": "SEMINAR",
                "room_name": "Ruang Seminar"
            },
            "date": "2026-11-11",
            "time": "16:00",
            "status": "Selesai",
            "reporter": "Kevin Sanjaya",
            "kept_at": "Dititipkan ke TU"
        }
    ]


def get_initial_matches() -> List[Dict[str, Any]]:
    return [
        {
            "match_id": "MATCH-0001",
            "lost_id": "LOST-2026-004",
            "found_id": "FOUND-2026-002",
            "score": 93.0,
            "status": "Dicocokkan",
            "date": "2026-11-15 11:00",
            "notes": "Botol minum Corkcicle biru milik Fajar cocok dengan tumbler temuan Pak Supri di Lobby"
        },
        {
            "match_id": "MATCH-0002",
            "lost_id": "LOST-2026-010",
            "found_id": "FOUND-2026-006",
            "score": 95.0,
            "status": "Diklaim",
            "date": "2026-11-15 11:30",
            "notes": "Kabel data merah Rian Kusuma telah diverifikasi dan siap diserahkan"
        },
        {
            "match_id": "MATCH-0003",
            "lost_id": "LOST-2026-005",
            "found_id": "FOUND-2026-004",
            "score": 98.0,
            "status": "Selesai",
            "date": "2026-11-13 16:00",
            "notes": "Tempat pensil Dewi Sartika telah dikembalikan oleh Ibu Ratna"
        },
        {
            "match_id": "MATCH-0004",
            "lost_id": "LOST-2026-006",
            "found_id": "FOUND-2026-005",
            "score": 96.0,
            "status": "Selesai",
            "date": "2026-11-12 18:30",
            "notes": "Dompet Bagus Wicaksono telah diambil di pos security"
        },
        {
            "match_id": "MATCH-0005",
            "lost_id": "LOST-2026-009",
            "found_id": "FOUND-2026-009",
            "score": 92.0,
            "status": "Selesai",
            "date": "2026-11-11 17:00",
            "notes": "Buku catatan Nadia Putri telah dikembalikan oleh Kevin"
        }
    ]


def populate_dummy_data_if_needed(data_manager):
    """Mengisi data dummy secara otomatis jika file data belum ada atau kosong."""
    import os
    import json

    need_populate = False
    if not os.path.exists(data_manager.lost_file) or os.path.getsize(data_manager.lost_file) <= 2:
        need_populate = True

    if need_populate:
        with open(data_manager.lost_file, "w", encoding="utf-8") as f:
            json.dump(get_initial_lost_items(), f, indent=2, ensure_ascii=False)

        with open(data_manager.found_file, "w", encoding="utf-8") as f:
            json.dump(get_initial_found_items(), f, indent=2, ensure_ascii=False)

        with open(data_manager.matches_file, "w", encoding="utf-8") as f:
            json.dump(get_initial_matches(), f, indent=2, ensure_ascii=False)

        data_manager.load_data()
        print("[LostBox] Berhasil memuat data dummy awal (19 laporan realistis).")
