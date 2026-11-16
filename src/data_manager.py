"""
data_manager.py
Modul manajemen penyimpanan data, validasi, dan agregasi statistik.
Menerapkan konsep Python:
- File Handling (JSON read/write)
- Exception Handling (Validasi form, FileNotFoundError, JSONDecodeError)
- Data Filtering & Aggregation (List, Dict, Tuple, Set)
- ID Generator
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from src.models import Location, Item, LostItem, FoundItem


class ValidationError(Exception):
    """Exception khusus untuk kegagalan validasi input pengguna."""
    pass


class DataManager:
    """
    Kelas DataManager bertugas menyimpan, memuat, memfilter, dan 
    menganalisis seluruh data laporan Lost & Found.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.lost_file = os.path.join(data_dir, "lost_items.json")
        self.found_file = os.path.join(data_dir, "found_items.json")
        self.matches_file = os.path.join(data_dir, "matches.json")
        self.settings_file = os.path.join(data_dir, "settings.json")

        self.lost_items: List[LostItem] = []
        self.found_items: List[FoundItem] = []
        self.matches: List[Dict[str, Any]] = []
        self.settings: Dict[str, Any] = {}

        # Pastikan folder data tersedia
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_settings()
        self.load_data()

    # ==========================================
    # SETTINGS & ROOM LOOKUP
    # ==========================================
    def load_settings(self) -> Dict[str, Any]:
        """Memuat konfigurasi gedung, ruangan, dan opsi dropdown."""
        if not os.path.exists(self.settings_file):
            self.settings = {
                "categories": [
                    "Elektronik", "Pakaian / Aksesoris", "Alat Tulis", 
                    "Botol / Tumbler", "Tas / Dompet", "Lainnya"
                ],
                "colors": [
                    "Hitam", "Putih", "Abu-abu", "Biru", "Merah", 
                    "Hijau", "Kuning", "Cokelat", "Pink", "Oranye", "Lainnya"
                ],
                "kept_at_options": [
                    "Dibawa pelapor", "Dititipkan ke TU", "Ditaruh di lokasi"
                ],
                "floors": {}
            }
            self.save_settings()
        else:
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"[DataManager] Warning memuat settings.json: {e}")
                self.settings = {}
        return self.settings

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DataManager] Gagal menyimpan settings.json: {e}")

    def get_room_list(self, floor: Optional[int] = None) -> List[Dict[str, Any]]:
        """Mendapatkan daftar ruangan per lantai atau seluruh lantai."""
        floors = self.settings.get("floors", {})
        rooms = []
        if floor is not None:
            fl_str = str(floor)
            if fl_str in floors:
                for r in floors[fl_str]:
                    rooms.append({"floor": floor, **r})
        else:
            for fl_str, fl_rooms in floors.items():
                fl_int = int(fl_str)
                for r in fl_rooms:
                    rooms.append({"floor": fl_int, **r})
        return rooms

    def get_room_by_code(self, room_code: str, floor: Optional[int] = None) -> Optional[Dict[str, Any]]:
        rooms = self.get_room_list(floor)
        for r in rooms:
            if r["code"].upper() == room_code.upper():
                return r
        return None

    # ==========================================
    # FILE PERSISTENCE (LOAD & SAVE)
    # ==========================================
    def load_data(self):
        """Memuat data JSON ke objek Python (OOP)."""
        # 1. Lost Items
        self.lost_items = []
        if os.path.exists(self.lost_file):
            try:
                with open(self.lost_file, "r", encoding="utf-8") as f:
                    raw_lost = json.load(f)
                    for item_data in raw_lost:
                        self.lost_items.append(LostItem.from_dict(item_data))
            except Exception as e:
                print(f"[DataManager] Gagal membaca lost_items.json: {e}")

        # 2. Found Items
        self.found_items = []
        if os.path.exists(self.found_file):
            try:
                with open(self.found_file, "r", encoding="utf-8") as f:
                    raw_found = json.load(f)
                    for item_data in raw_found:
                        self.found_items.append(FoundItem.from_dict(item_data))
            except Exception as e:
                print(f"[DataManager] Gagal membaca found_items.json: {e}")

        # 3. Matches
        self.matches = []
        if os.path.exists(self.matches_file):
            try:
                with open(self.matches_file, "r", encoding="utf-8") as f:
                    self.matches = json.load(f)
            except Exception as e:
                print(f"[DataManager] Gagal membaca matches.json: {e}")

    def save_data(self):
        """Menyimpan seluruh data ke file JSON."""
        # Save Lost Items
        try:
            with open(self.lost_file, "w", encoding="utf-8") as f:
                json.dump([item.to_dict() for item in self.lost_items], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DataManager] Error saving lost items: {e}")

        # Save Found Items
        try:
            with open(self.found_file, "w", encoding="utf-8") as f:
                json.dump([item.to_dict() for item in self.found_items], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DataManager] Error saving found items: {e}")

        # Save Matches
        try:
            with open(self.matches_file, "w", encoding="utf-8") as f:
                json.dump(self.matches, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DataManager] Error saving matches: {e}")

    # ==========================================
    # ID GENERATOR
    # ==========================================
    def generate_id(self, item_type: str = "LOST") -> str:
        """
        Membuat ID unik berformat: PREFIX-YYYY-XXX (contoh: LOST-2026-001)
        Menerapkan manipulasi string dan perulangan.
        """
        year = datetime.now().year
        prefix = item_type.upper()
        existing_items = self.lost_items if prefix == "LOST" else self.found_items
        
        # Ekstrak nomor urut tertinggi tahun ini
        max_num = 0
        regex = rf"^{prefix}-{year}-(\d+)$"
        for item in existing_items:
            match = re.match(regex, item.id)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

        new_num = max_num + 1
        return f"{prefix}-{year}-{new_num:03d}"

    # ==========================================
    # INPUT VALIDATION
    # ==========================================
    @classmethod
    def validate_item_input(cls, data: Dict[str, Any]) -> None:
        """
        Validasi integritas data form.
        Melempar ValidationError jika ada field tidak valid.
        """
        if not data.get("reporter", "").strip():
            raise ValidationError("Nama pelapor wajib diisi!")

        if not data.get("name", "").strip():
            raise ValidationError("Nama barang wajib diisi!")

        if not data.get("category", "").strip():
            raise ValidationError("Kategori barang wajib dipilih!")

        if not data.get("color", "").strip():
            raise ValidationError("Warna dominan wajib dipilih!")

        # Validasi format tanggal YYYY-MM-DD
        date_str = data.get("date", "").strip()
        if not date_str:
            raise ValidationError("Tanggal laporan wajib diisi!")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Format tanggal tidak valid! Gunakan format YYYY-MM-DD (contoh: 2026-11-14)")

        # Validasi format waktu HH:MM
        time_str = data.get("time", "").strip()
        if time_str:
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                raise ValidationError("Format waktu tidak valid! Gunakan format HH:MM (contoh: 14:30)")

        # Validasi lokasi
        loc = data.get("location")
        if not loc:
            raise ValidationError("Lokasi ruangan harus ditentukan!")
        if isinstance(loc, dict):
            if not loc.get("room_code"):
                raise ValidationError("Kode ruangan lokasi tidak boleh kosong!")
        elif isinstance(loc, Location):
            if not loc.room_code:
                raise ValidationError("Kode ruangan lokasi tidak boleh kosong!")
        else:
            raise ValidationError("Format objek lokasi tidak sesuai!")

    # ==========================================
    # CRUD OPERATIONS
    # ==========================================
    def add_lost_item(self, item_dict: Dict[str, Any]) -> LostItem:
        """Menambahkan laporan barang hilang baru setelah validasi."""
        self.validate_item_input(item_dict)
        if "id" not in item_dict or not item_dict["id"]:
            item_dict["id"] = self.generate_id("LOST")

        new_item = LostItem.from_dict(item_dict)
        self.lost_items.append(new_item)
        self.save_data()
        return new_item

    def add_found_item(self, item_dict: Dict[str, Any]) -> FoundItem:
        """Menambahkan laporan barang temuan baru setelah validasi."""
        self.validate_item_input(item_dict)
        if "id" not in item_dict or not item_dict["id"]:
            item_dict["id"] = self.generate_id("FOUND")

        new_item = FoundItem.from_dict(item_dict)
        self.found_items.append(new_item)
        self.save_data()
        return new_item

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        """Mencari barang berdasarkan ID."""
        for item in self.lost_items:
            if item.id == item_id:
                return item
        for item in self.found_items:
            if item.id == item_id:
                return item
        return None

    def update_item_status(self, item_id: str, new_status: str) -> bool:
        """Mengubah status barang (Dilaporkan -> Dicocokkan -> Diklaim -> Selesai)."""
        item = self.get_item_by_id(item_id)
        if item:
            item.update_status(new_status)
            self.save_data()
            return True
        return False

    def delete_item(self, item_id: str) -> bool:
        """Menghapus item berdasarkan ID."""
        for i, item in enumerate(self.lost_items):
            if item.id == item_id:
                self.lost_items.pop(i)
                self.save_data()
                return True
        for i, item in enumerate(self.found_items):
            if item.id == item_id:
                self.found_items.pop(i)
                self.save_data()
                return True
        return False

    # ==========================================
    # MATCH RECORD OPERATIONS
    # ==========================================
    def record_match(self, lost_id: str, found_id: str, score: float, notes: str = "") -> Dict[str, Any]:
        """Merekam konfirmasi kecocokan antara lost dan found item."""
        match_id = f"MATCH-{len(self.matches) + 1:04d}"
        record = {
            "match_id": match_id,
            "lost_id": lost_id,
            "found_id": found_id,
            "score": score,
            "status": "Dicocokkan",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "notes": notes,
        }
        self.matches.append(record)
        # Update status kedua barang menjadi Dicocokkan
        self.update_item_status(lost_id, "Dicocokkan")
        self.update_item_status(found_id, "Dicocokkan")
        self.save_data()
        return record

    def update_match_status(self, match_id: str, new_status: str):
        """Memperbarui status transaksi kecocokan (Dicocokkan -> Diklaim -> Selesai)."""
        for m in self.matches:
            if m["match_id"] == match_id:
                m["status"] = new_status
                if new_status == "Bukan barang yang sama":
                    # Kembalikan kedua barang ke 'Dilaporkan'
                    self.update_item_status(m["lost_id"], "Dilaporkan")
                    self.update_item_status(m["found_id"], "Dilaporkan")
                elif new_status in ("Diklaim", "Selesai"):
                    self.update_item_status(m["lost_id"], new_status)
                    self.update_item_status(m["found_id"], new_status)
                self.save_data()
                return True
        return False

    # ==========================================
    # DATA FILTERING & QUERYING
    # ==========================================
    def filter_items(
        self,
        item_type: str = "ALL",  # "ALL", "LOST", "FOUND"
        category: Optional[str] = None,
        color: Optional[str] = None,
        floor: Optional[int] = None,
        room_code: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> List[Item]:
        """
        Fungsi fleksibel untuk filter daftar barang berdasarkan berbagai kriteria.
        Menerapkan perulangan, percabangan, dan list comprehension.
        """
        candidates: List[Item] = []
        if item_type.upper() in ("ALL", "LOST"):
            candidates.extend(self.lost_items)
        if item_type.upper() in ("ALL", "FOUND"):
            candidates.extend(self.found_items)

        results = []
        kw_clean = keyword.strip().lower() if keyword else None

        for item in candidates:
            # Filter Kategori
            if category and category != "Semua Kategori" and item.category != category:
                continue

            # Filter Warna
            if color and color != "Semua Warna" and item.color != color:
                continue

            # Filter Lantai
            if floor is not None and item.location.floor != floor:
                continue

            # Filter Ruangan
            if room_code and room_code != "Semua Ruangan" and item.location.room_code.upper() != room_code.upper():
                continue

            # Filter Status
            if status and status != "Semua Status" and item.status != status:
                continue

            # Filter Keyword (Pencarian nama, deskripsi, pelapor, id)
            if kw_clean:
                search_space = f"{item.id} {item.name} {item.description} {item.reporter} {item.location.room_name}".lower()
                if kw_clean not in search_space:
                    continue

            results.append(item)

        # Urutkan berdasarkan tanggal terbaru
        return sorted(results, key=lambda x: (x.date, x.time), reverse=True)

    def get_room_item_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Menghitung jumlah laporan aktif per ruangan untuk ditampilkan di badge peta lantai.
        Mengembalikan dict: {room_code: {"lost": x, "found": y, "total": z}}
        """
        counts: Dict[str, Dict[str, int]] = {}
        for r in self.get_room_list():
            counts[r["code"]] = {"lost": 0, "found": 0, "total": 0}

        # Hanya hitung laporan yang aktif (belum selesai)
        for item in self.lost_items:
            if item.status in ("Dilaporkan", "Dicocokkan", "Diklaim"):
                code = item.location.room_code
                if code in counts:
                    counts[code]["lost"] += 1
                    counts[code]["total"] += 1

        for item in self.found_items:
            if item.status in ("Dilaporkan", "Dicocokkan", "Diklaim"):
                code = item.location.room_code
                if code in counts:
                    counts[code]["found"] += 1
                    counts[code]["total"] += 1

        return counts

    # ==========================================
    # STATISTICS AGGREGATOR
    # ==========================================
    def get_statistics(self) -> Dict[str, Any]:
        """
        Menghitung seluruh metrik analitik dashboard:
        - Total laporan aktif (lost vs found)
        - Tingkat pengembalian (persentase barang berhasil kembali)
        - Hotspot lokasi (ruangan paling sering kehilangan barang)
        - Kategori terbanyak
        - Tren waktu pelaporan (per jam / per hari)
        """
        total_lost = len(self.lost_items)
        total_found = len(self.found_items)
        total_reports = total_lost + total_found

        active_lost = sum(1 for i in self.lost_items if i.status in ("Dilaporkan", "Dicocokkan", "Diklaim"))
        active_found = sum(1 for i in self.found_items if i.status in ("Dilaporkan", "Dicocokkan", "Diklaim"))
        active_total = active_lost + active_found

        matched_count = sum(1 for i in self.lost_items if i.status == "Dicocokkan") + \
                        sum(1 for i in self.found_items if i.status == "Dicocokkan")

        claimed_count = sum(1 for i in self.lost_items if i.status == "Diklaim") + \
                        sum(1 for i in self.found_items if i.status == "Diklaim")

        completed_lost = sum(1 for i in self.lost_items if i.status == "Selesai")
        completed_found = sum(1 for i in self.found_items if i.status == "Selesai")
        completed_total = completed_lost + completed_found

        # Tingkat pengembalian (%)
        return_rate = (completed_total / total_reports * 100.0) if total_reports > 0 else 0.0

        # Hotspot Lokasi (Lost Items per Ruangan)
        hotspots: Dict[str, int] = {}
        for item in self.lost_items:
            room_label = f"{item.location.room_name} (Lt.{item.location.floor})"
            hotspots[room_label] = hotspots.get(room_label, 0) + 1

        sorted_hotspots = sorted(hotspots.items(), key=lambda x: x[1], reverse=True)

        # Kategori Terbanyak (Lost vs Found)
        category_counts: Dict[str, Dict[str, int]] = {}
        for cat in self.settings.get("categories", []):
            category_counts[cat] = {"lost": 0, "found": 0, "total": 0}

        for item in self.lost_items:
            cat = item.category
            if cat not in category_counts:
                category_counts[cat] = {"lost": 0, "found": 0, "total": 0}
            category_counts[cat]["lost"] += 1
            category_counts[cat]["total"] += 1

        for item in self.found_items:
            cat = item.category
            if cat not in category_counts:
                category_counts[cat] = {"lost": 0, "found": 0, "total": 0}
            category_counts[cat]["found"] += 1
            category_counts[cat]["total"] += 1

        # Tren Waktu (Distribusi Jam Pelaporan)
        hour_counts: Dict[str, int] = {}
        for h in range(7, 21):  # Dari jam 07:00 sampai 20:00
            hour_counts[f"{h:02d}:00"] = 0

        for item in self.lost_items + self.found_items:
            if item.time:
                try:
                    hour_str = item.time.split(":")[0]
                    formatted_hour = f"{int(hour_str):02d}:00"
                    if formatted_hour in hour_counts:
                        hour_counts[formatted_hour] += 1
                    else:
                        hour_counts[formatted_hour] = 1
                except Exception:
                    pass

        # Tren Hari (Senin - Minggu)
        day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        day_counts: Dict[str, int] = {d: 0 for d in day_names}
        for item in self.lost_items + self.found_items:
            if item.date:
                try:
                    dt = datetime.strptime(item.date, "%Y-%m-%d")
                    day_name = day_names[dt.weekday()]
                    day_counts[day_name] += 1
                except Exception:
                    pass

        return {
            "total_reports": total_reports,
            "total_lost": total_lost,
            "total_found": total_found,
            "active_total": active_total,
            "active_lost": active_lost,
            "active_found": active_found,
            "matched_count": matched_count,
            "claimed_count": claimed_count,
            "completed_total": completed_total,
            "completed_lost": completed_lost,
            "completed_found": completed_found,
            "return_rate": round(return_rate, 1),
            "hotspots": sorted_hotspots,
            "categories": category_counts,
            "hourly_trend": hour_counts,
            "daily_trend": day_counts,
        }
