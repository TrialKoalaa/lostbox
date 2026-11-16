"""
home_view.py
Halaman Beranda / Dashboard Utama LostBox.
Menampilkan summary cards, match terbaru, laporan terbaru, dan quick action buttons.
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import customtkinter as ctk
from typing import Dict, Any, Callable
from src.ui.dialogs import MatchReviewDialog, ItemDetailDialog


class HomeView(ctk.CTkFrame):
    """
    Tampilan Dashboard Utama (Home) LostBox.
    """

    def __init__(self, parent, data_manager, match_engine, on_navigate_callback: Callable):
        super().__init__(parent, fg_color="transparent")
        self.dm = data_manager
        self.engine = match_engine
        self.on_navigate = on_navigate_callback

        self._build_ui()

    def _build_ui(self):
        # Scrollable container for whole home page
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. Welcome Header Banner
        banner = ctk.CTkFrame(self.scroll, fg_color=("#1E3A8A", "#0F172A"), corner_radius=12)
        banner.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            banner,
            text="SELAMAT DATANG DI LOSTBOX",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#60A5FA",
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            banner,
            text="Sistem Lost & Found Digital Gedung Prodi Sains Data • 'Barang hilang? Cek LostBox dulu.'",
            font=ctk.CTkFont(size=13),
            text_color="#E2E8F0",
        ).pack(anchor="w", padx=20, pady=(0, 18))

        # 2. KPI Cards: [Barang Hilang] [Barang Temuan] [Berhasil Kembali]
        self.kpi_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.kpi_container.pack(fill="x", pady=(0, 16))

        # 3. Quick Action Buttons
        act_box = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray17"), corner_radius=10)
        act_box.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(act_box, text="⚡ Aksi Cepat:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=16, pady=12)

        btn_lost = ctk.CTkButton(
            act_box,
            text="📝 Lapor Barang Hilang",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda: self.on_navigate("lost"),
            height=34,
        )
        btn_lost.pack(side="left", padx=(0, 10))

        btn_found = ctk.CTkButton(
            act_box,
            text="📦 Lapor Temuan",
            fg_color="#059669",
            hover_color="#047857",
            command=lambda: self.on_navigate("found"),
            height=34,
        )
        btn_found.pack(side="left", padx=(0, 10))

        btn_map = ctk.CTkButton(
            act_box,
            text="🗺️ Buka Peta Gedung",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=lambda: self.on_navigate("map"),
            height=34,
        )
        btn_map.pack(side="left")

        # 4. Section: MATCH TERBARU (Kecocokan Otomatis)
        self.match_section = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray17"), corner_radius=10)
        self.match_section.pack(fill="x", pady=(0, 16))

        # 5. Section: LAPORAN TERBARU
        self.report_section = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray17"), corner_radius=10)
        self.report_section.pack(fill="x", pady=(0, 10))

        self.refresh_home()

    def refresh_home(self):
        """Memuat ulang data statistik, match, dan laporan terbaru."""
        stats = self.dm.get_statistics()

        # Render KPI Cards
        for child in self.kpi_container.winfo_children():
            child.destroy()

        cards = [
            ("🔴  Barang Hilang Aktif", str(stats["active_lost"]), "#EF4444", "lost"),
            ("🟢  Barang Temuan Aktif", str(stats["active_found"]), "#10B981", "found"),
            ("✅  Berhasil Kembali", str(stats["completed_total"]), "#3B82F6", "search"),
        ]

        for i, (title, val, col, target_nav) in enumerate(cards):
            c_frame = ctk.CTkFrame(self.kpi_container, fg_color=("gray92", "gray18"), corner_radius=10, height=85)
            c_frame.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 10, 0))
            c_frame.pack_propagate(False)

            ctk.CTkLabel(c_frame, text=title, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
            ctk.CTkLabel(c_frame, text=val, font=ctk.CTkFont(size=24, weight="bold"), text_color=col).pack(pady=(0, 10))

        # Render Match Section
        for child in self.match_section.winfo_children():
            child.destroy()

        ctk.CTkLabel(
            self.match_section,
            text="🔔 KECOCOKAN TERBARU (AUTO-MATCHER)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#D97706",
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Cari semua match aktif
        self.engine.set_items(self.dm.lost_items, self.dm.found_items)
        active_matches = []
        for lost in self.dm.lost_items:
            if lost.status in ("Dilaporkan", "Dicocokkan"):
                found_candidates = self.engine.find_matches(lost, min_score=50.0)
                for m in found_candidates:
                    active_matches.append(m)

        # Hapus duplikat dan ambil top 4
        seen_pairs = set()
        top_matches = []
        for m in sorted(active_matches, key=lambda x: x["score"], reverse=True):
            pair_key = (m["target_id"], m["candidate_id"])
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                top_matches.append(m)
            if len(top_matches) >= 4:
                break

        if not top_matches:
            empty_m = ctk.CTkLabel(
                self.match_section,
                text="Belum ada kecocokan aktif saat ini. Sistem akan mendeteksi saat ada laporan baru.",
                font=ctk.CTkFont(size=12),
                text_color="gray50",
            )
            empty_m.pack(padx=16, pady=(4, 14))
        else:
            for m in top_matches:
                m_row = ctk.CTkFrame(self.match_section, fg_color=("gray85", "gray22"), corner_radius=6)
                m_row.pack(fill="x", padx=16, pady=4)

                lost_name = m["target_item"].name
                found_name = m["candidate_item"].name
                score = m["score"]

                text_str = f"🔔  {lost_name}  ↔  {found_name}  ({score}% cocok)"
                ctk.CTkLabel(
                    m_row,
                    text=text_str,
                    font=ctk.CTkFont(size=12, weight="bold"),
                ).pack(side="left", padx=12, pady=8)

                btn_rev = ctk.CTkButton(
                    m_row,
                    text="Review Match",
                    height=26,
                    width=100,
                    fg_color="#D97706",
                    hover_color="#B45309",
                    command=lambda match_item=m: self._open_match_dialog(match_item),
                )
                btn_rev.pack(side="right", padx=10, pady=6)

            ctk.CTkLabel(self.match_section, text="").pack(pady=2)

        # Render Recent Reports Section
        for child in self.report_section.winfo_children():
            child.destroy()

        ctk.CTkLabel(
            self.report_section,
            text="📋 LAPORAN TERAKHIR MASUK",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(12, 6))

        all_items = self.dm.filter_items(item_type="ALL")
        recent_items = all_items[:5]

        if not recent_items:
            ctk.CTkLabel(
                self.report_section,
                text="Belum ada laporan barang.",
                font=ctk.CTkFont(size=12),
                text_color="gray50",
            ).pack(padx=16, pady=(4, 14))
        else:
            for item in recent_items:
                r_card = ctk.CTkFrame(self.report_section, fg_color=("gray85", "gray22"), corner_radius=6)
                r_card.pack(fill="x", padx=16, pady=4)

                is_lost = (item.item_type == "LOST")
                icon_col = "#EF4444" if is_lost else "#10B981"
                prefix = "🔴 Hilang" if is_lost else "🟢 Temuan"

                ctk.CTkLabel(
                    r_card,
                    text=f"{prefix} • {item.name}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                ).pack(side="left", padx=12, pady=8)

                loc_str = f"📍 {item.location.room_name} • {item.date}"
                ctk.CTkLabel(
                    r_card,
                    text=loc_str,
                    font=ctk.CTkFont(size=11),
                    text_color=("gray40", "gray70"),
                ).pack(side="left", padx=8)

                btn_view = ctk.CTkButton(
                    r_card,
                    text="Detail",
                    height=24,
                    width=70,
                    fg_color=("#3B82F6", "#2563EB"),
                    command=lambda it=item: self._open_item_dialog(it),
                )
                btn_view.pack(side="right", padx=10, pady=6)

            ctk.CTkLabel(self.report_section, text="").pack(pady=2)

    def _open_match_dialog(self, match_data):
        MatchReviewDialog(
            self.winfo_toplevel(),
            match_data=match_data,
            data_manager=self.dm,
            on_action_callback=self.refresh_home,
        )

    def _open_item_dialog(self, item):
        ItemDetailDialog(
            self.winfo_toplevel(),
            item=item,
            data_manager=self.dm,
            on_update_callback=self.refresh_home,
        )
