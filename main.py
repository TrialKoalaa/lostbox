"""
=============================================================================
PROJEK PEMROGRAMAN DASAR
LostBox — Sains Data Edition
Tagline: "Barang hilang? Cek LostBox dulu."

Anggota Tim & Pembagian Tugas:
1. Anggota 1: Backend & Data Engine (Class Item, LostItem, FoundItem, Location, DataManager, File Handling, JSON)
2. Anggota 2: Match Engine & Statistics (Scoring Algorithm, Lifecycle Status Tracker, Analytics Aggregator)
3. Anggota 3: GUI & Floor Plan (CustomTkinter, Interactive Map Grid, Search & Filter, Matplotlib Visualization)
=============================================================================
"""

import sys
import os
import tempfile

# Pastikan direktori kerja saat ini ada di sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Konfigurasi temporary directory untuk Matplotlib agar bebas permission error
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()


def run_cli_demo():
    """
    Mode demonstrasi CLI terminal untuk pengujian logika secara menyeluruh
    tanpa membutuhkan display window GUI.
    """
    from src.data_manager import DataManager
    from src.match_engine import MatchEngine
    from src.sample_data import populate_dummy_data_if_needed

    print("=" * 65)
    print("      LOSTBOX — SAINS DATA EDITION (CLI DEMONSTRATION)")
    print("=" * 65)

    dm = DataManager(data_dir="data")
    populate_dummy_data_if_needed(dm)
    engine = MatchEngine(dm.lost_items, dm.found_items)

    print(f"\n[1] DATA STATUS:")
    print(f"    - Total Barang Hilang   : {len(dm.lost_items)} laporan")
    print(f"    - Total Barang Temuan   : {len(dm.found_items)} laporan")
    print(f"    - Total Riwayat Match   : {len(dm.matches)} transaksi")

    print("\n[2] SIMULASI SKENARIO PRESENTASI (AHMAD & BUDI - CHARGER ASUS):")
    ahmad_item = dm.get_item_by_id("LOST-2026-001")
    budi_item = dm.get_item_by_id("FOUND-2026-001")

    if ahmad_item and budi_item:
        print(f"    • Pelapor Hilang : {ahmad_item.reporter} ({ahmad_item.name} di {ahmad_item.location})")
        print(f"    • Pelapor Temuan : {budi_item.reporter} ({budi_item.name} di {budi_item.location})")

        score, breakdown, reasons = engine.calculate_score(ahmad_item, budi_item)
        print(f"\n    >>> HASIL AUTO-MATCHER: {score}% COCOK <<<")
        print("    Rincian Skor:")
        for k, v in breakdown.items():
            print(f"      - {k.capitalize():10}: {v}%")
        print("    Alasan Pencocokan:")
        for r in reasons:
            print(f"      - {r}")

    print("\n[3] ANALISIS HOTSPOT KEHILANGAN TERBANYAK:")
    stats = dm.get_statistics()
    for idx, (room, count) in enumerate(stats["hotspots"][:3], 1):
        print(f"    {idx}. {room}: {count} kasus kehilangan")

    print(f"\n[4] TINGKAT PENGEMBALIAN BARANG:")
    print(f"    - Persentase Berhasil Kembali: {stats['return_rate']}%")
    print(f"    - Total Selesai: {stats['completed_total']} barang")

    print("\n[5] STATUS LANTAI & RUANGAN (FLOOR PLAN SUMMARY):")
    counts = dm.get_room_item_counts()
    for code, c in counts.items():
        if c["total"] > 0:
            print(f"    - Ruangan {code:10}: {c['lost']} hilang, {c['found']} temuan (Total: {c['total']})")

    print("\n" + "=" * 65)
    print("Demo CLI Selesai dengan Sukses!")
    print("=" * 65)


def run_gui():
    """Menjalankan aplikasi grafis interaktif CustomTkinter."""
    from src.ui.app import LostBoxApp

    app = LostBoxApp()
    app.mainloop()


if __name__ == "__main__":
    # Dukung argumen terminal --cli untuk pengujian tanpa GUI
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--cli", "-c", "--demo"):
        run_cli_demo()
    else:
        try:
            run_gui()
        except Exception as e:
            # Jika lingkungan terminal tidak memiliki active display server
            print(f"[LostBox] Catatan GUI: {e}")
            print("[LostBox] Menjalankan fallback demonstrasi CLI...")
            run_cli_demo()
