"""
app.py
Aplikasi Utama LostBox GUI (CustomTkinter).
Menghubungkan seluruh modul backend, tampilan views, navigasi sidebar, dan status bar.
"""

import sys
import os

# Tambahkan root direktori projek ke sys.path agar bisa dijalankan langsung
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import customtkinter as ctk
from tkinter import messagebox

from src.data_manager import DataManager
from src.match_engine import MatchEngine
from src.sample_data import populate_dummy_data_if_needed

from src.ui.home_view import HomeView
from src.ui.report_view import ReportView
from src.ui.map_view import MapView
from src.ui.search_view import SearchView
from src.ui.stats_view import StatsView


class LostBoxApp(ctk.CTk):
    """
    Jendela Utama Aplikasi LostBox — Sains Data Edition.
    """

    def __init__(self):
        super().__init__()

        # Inisialisasi Backend
        self.dm = DataManager(data_dir="data")
        populate_dummy_data_if_needed(self.dm)

        self.engine = MatchEngine(self.dm.lost_items, self.dm.found_items)

        # Konfigurasi Window
        self.title("LostBox — Sains Data Edition (Prodi Sains Data)")
        self.geometry("1180x760")
        self.minsize(1000, 680)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.active_view_name = "home"
        self.views = {}

        self._build_layout()
        self.navigate("home")
        self.update_status_bar()

    def _build_layout(self):
        # 1. Top Header Bar
        header = ctk.CTkFrame(self, height=54, corner_radius=0, fg_color=("#1E293B", "#0F172A"))
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Logo and Title
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)

        ctk.CTkLabel(
            title_box,
            text="📦 LostBox",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#60A5FA",
        ).pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="— Sains Data Edition",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=8)

        # Right Header: Theme Mode Switcher + Reset Data Button
        right_header = ctk.CTkFrame(header, fg_color="transparent")
        right_header.pack(side="right", padx=16)

        btn_reset_demo = ctk.CTkButton(
            right_header,
            text="🔄 Muat Ulang Data Demo",
            font=ctk.CTkFont(size=11),
            height=28,
            width=150,
            fg_color=("#475569", "#334155"),
            hover_color=("#334155", "#1E293B"),
            command=self._confirm_reload_demo_data,
        )
        btn_reset_demo.pack(side="left", padx=(0, 12))

        self.theme_switch = ctk.CTkSwitch(
            right_header,
            text="Dark Mode",
            font=ctk.CTkFont(size=11),
            command=self._toggle_theme,
        )
        self.theme_switch.select()
        self.theme_switch.pack(side="left")

        # 2. Bottom Status Bar
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0, fg_color=("gray90", "gray14"))
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="Memuat status...",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray75"),
        )
        self.lbl_status.pack(side="left", padx=16)

        ver_lbl = ctk.CTkLabel(
            self.status_bar,
            text="Tugas Projek Pemrograman Dasar • Prodi Sains Data 2026",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50"),
        )
        ver_lbl.pack(side="right", padx=16)

        # 3. Middle Area: Sidebar (Left) + Content (Right)
        middle_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        middle_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(middle_container, width=210, corner_radius=0, fg_color=("gray95", "gray16"))
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # Content Area
        self.content_area = ctk.CTkFrame(middle_container, fg_color="transparent", corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

    def _build_sidebar(self):
        ctk.CTkLabel(
            self.sidebar,
            text="MENU UTAMA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray40", "gray60"),
        ).pack(anchor="w", padx=18, pady=(20, 10))

        self.nav_buttons = {}

        menus = [
            ("home", "🏠  Home", "Dashboard Utama"),
            ("lost", "🔴  Lost Items", "Lapor & Daftar Hilang"),
            ("found", "🟢  Found Items", "Lapor & Daftar Temuan"),
            ("search", "🔍  Search", "Pencarian & Filter"),
            ("map", "🗺️  Floor Plan", "Peta Lantai Gedung"),
            ("stats", "📊  Statistics", "Statistik & Analitik"),
        ]

        for code, label, subtext in menus:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                height=42,
                fg_color="transparent",
                text_color=("gray20", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda c=code: self.navigate(c),
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[code] = btn

    def _toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

        # Segarkan chart jika sedang di halaman stats
        if self.active_view_name == "stats" and "stats" in self.views:
            self.views["stats"].refresh_stats()

    def navigate(self, view_name: str):
        """Berpindah tampilan halaman di Content Area."""
        self.active_view_name = view_name

        # Highlight tombol sidebar yang aktif
        for code, btn in self.nav_buttons.items():
            if code == view_name:
                btn.configure(fg_color=("#3B82F6", "#1E3A8A"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray20", "gray90"))

        # Hapus tampilan konten lama
        for child in self.content_area.winfo_children():
            child.pack_forget()

        # Inisialisasi atau tampilkan view
        self.engine.set_items(self.dm.lost_items, self.dm.found_items)

        if view_name == "home":
            if "home" not in self.views:
                self.views["home"] = HomeView(self.content_area, self.dm, self.engine, on_navigate_callback=self.navigate)
            else:
                self.views["home"].refresh_home()
            self.views["home"].pack(fill="both", expand=True)

        elif view_name == "lost":
            # Selalu buat baru agar form ter-reset dan data tersinkron
            self.views["lost"] = ReportView(self.content_area, self.dm, self.engine, report_type="LOST", on_change_callback=self.update_status_bar)
            self.views["lost"].pack(fill="both", expand=True)

        elif view_name == "found":
            self.views["found"] = ReportView(self.content_area, self.dm, self.engine, report_type="FOUND", on_change_callback=self.update_status_bar)
            self.views["found"].pack(fill="both", expand=True)

        elif view_name == "search":
            self.views["search"] = SearchView(self.content_area, self.dm, self.engine, on_update_callback=self.update_status_bar)
            self.views["search"].pack(fill="both", expand=True)

        elif view_name == "map":
            if "map" not in self.views:
                self.views["map"] = MapView(self.content_area, self.dm, self.engine, on_navigate_callback=self.navigate)
            else:
                self.views["map"].refresh_map()
            self.views["map"].pack(fill="both", expand=True)

        elif view_name == "stats":
            if "stats" not in self.views:
                self.views["stats"] = StatsView(self.content_area, self.dm)
            else:
                self.views["stats"].refresh_stats()
            self.views["stats"].pack(fill="both", expand=True)

        self.update_status_bar()

    def update_status_bar(self):
        """Memperbarui teks di status bar bawah."""
        stats = self.dm.get_statistics()
        active = stats["active_total"]
        matched = stats["matched_count"]
        completed = stats["completed_total"]
        self.lbl_status.configure(
            text=f"Status: {active} Laporan Aktif  |  {matched} Status Dicocokkan  |  {completed} Berhasil Dikembalikan  |  Return Rate: {stats['return_rate']}%"
        )

    def _confirm_reload_demo_data(self):
        confirm = messagebox.askyesno(
            "Konfirmasi Reset Data",
            "Apakah Anda yakin ingin memuat ulang 19 data dummy awal?\nSemua data baru yang belum disimpan terpisah akan ter-reset.",
        )
        if confirm:
            import os
            # Kosongkan file lalu populate ulang
            if os.path.exists(self.dm.lost_file):
                os.remove(self.dm.lost_file)
            populate_dummy_data_if_needed(self.dm)
            messagebox.showinfo("Berhasil", "Data demo realistis berhasil dimuat ulang.")
            self.navigate(self.active_view_name)


if __name__ == "__main__":
    app = LostBoxApp()
    app.mainloop()

