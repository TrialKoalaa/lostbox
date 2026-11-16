"""
stats_view.py
Halaman Statistik & Visualisasi Data (Matplotlib embedded in CustomTkinter).
Menganalisis hotspot lokasi, kategori terpopuler, return rate, dan tren waktu.
"""

import os
import sys
import tempfile

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Pastikan cache matplotlib menggunakan folder temp yang dapat ditulisi
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

import customtkinter as ctk
from typing import Dict, Any

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class StatsView(ctk.CTkFrame):
    """
    Halaman statistik dan visualisasi analitik LostBox.
    """

    def __init__(self, parent, data_manager):
        super().__init__(parent, fg_color="transparent")
        self.dm = data_manager
        self.current_canvas = None

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header_frame,
            text="📊 Statistik & Analisis Kehilangan Barang",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Wawasan analitik data lost & found Gedung Prodi Sains Data untuk evaluasi keamanan dan penanganan.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
        ).pack(anchor="w")

        # 2. Top Summary KPI Cards
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=(4, 10))

        # 3. Chart Category Switcher (Tabs)
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.pack(fill="x", padx=20, pady=(0, 6))

        self.chart_selector = ctk.CTkSegmentedButton(
            tab_bar,
            values=[
                "🔥 Hotspot Lokasi",
                "📦 Kategori Barang",
                "📈 Tingkat Pengembalian",
                "⏰ Tren Waktu",
            ],
            command=self._on_chart_change,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
        )
        self.chart_selector.set("🔥 Hotspot Lokasi")
        self.chart_selector.pack(side="left")

        btn_refresh = ctk.CTkButton(
            tab_bar,
            text="🔄 Segarkan Grafik",
            width=120,
            command=self.refresh_stats,
        )
        btn_refresh.pack(side="right")

        # 4. Canvas Container for Matplotlib
        self.chart_container = ctk.CTkFrame(self, fg_color=("gray92", "gray17"), corner_radius=10)
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.refresh_stats()

    def refresh_stats(self):
        stats = self.dm.get_statistics()
        self._render_kpi_cards(stats)
        self._render_current_chart(stats)

    def _render_kpi_cards(self, stats: Dict[str, Any]):
        for child in self.kpi_frame.winfo_children():
            child.destroy()

        cards_data = [
            ("Total Laporan", str(stats["total_reports"]), "#3B82F6"),
            ("Kasus Aktif", str(stats["active_total"]), "#F59E0B"),
            ("Tingkat Pengembalian", f"{stats['return_rate']}%", "#10B981"),
            ("Hotspot Tertinggi", stats["hotspots"][0][0].split(" (")[0] if stats["hotspots"] else "-", "#EF4444"),
        ]

        for i, (title, val, color) in enumerate(cards_data):
            card = ctk.CTkFrame(self.kpi_frame, fg_color=("gray92", "gray19"), corner_radius=8, height=72)
            card.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 6, 0))
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color=("gray40", "gray70")).pack(pady=(8, 1))
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack(pady=(0, 8))

    def _on_chart_change(self, val):
        stats = self.dm.get_statistics()
        self._render_current_chart(stats)

    def _render_current_chart(self, stats: Dict[str, Any]):
        # Clear existing canvas
        for child in self.chart_container.winfo_children():
            child.destroy()

        if not HAS_MATPLOTLIB:
            notice_frame = ctk.CTkFrame(self.chart_container, fg_color="transparent")
            notice_frame.pack(expand=True, pady=40)
            ctk.CTkLabel(
                notice_frame,
                text="📊 Pustaka 'matplotlib' belum terpasang di Python ini.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#F59E0B",
            ).pack(pady=4)
            ctk.CTkLabel(
                notice_frame,
                text="Jalankan: pip install matplotlib\n(Kartu ringkasan KPI di atas tetap aktif dan akurat)",
                font=ctk.CTkFont(size=12),
                text_color="gray60",
                justify="center",
            ).pack(pady=4)
            return

        choice = self.chart_selector.get()

        # Modern Matplotlib style
        plt.close("all")
        is_dark = (ctk.get_appearance_mode().lower() == "dark")
        bg_color = "#1E293B" if is_dark else "#F8FAFC"
        text_color = "#F1F5F9" if is_dark else "#0F172A"
        grid_color = "#334155" if is_dark else "#E2E8F0"

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        if "Hotspot" in choice:
            self._plot_hotspots(ax, stats, text_color, grid_color)
        elif "Kategori" in choice:
            self._plot_categories(ax, stats, text_color, grid_color)
        elif "Pengembalian" in choice:
            self._plot_return_rate(ax, stats, text_color, bg_color)
        else:
            self._plot_time_trend(ax, stats, text_color, grid_color)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.current_canvas = canvas

    def _plot_hotspots(self, ax, stats, text_color, grid_color):
        hotspots = stats["hotspots"][:6]
        if not hotspots:
            ax.text(0.5, 0.5, "Belum ada data lokasi kehilangan", ha="center", va="center", color=text_color)
            return

        rooms = [h[0] for h in reversed(hotspots)]
        counts = [h[1] for h in reversed(hotspots)]

        bars = ax.barh(rooms, counts, color="#EF4444", height=0.6)
        ax.set_title("Hotspot Lokasi Paling Rawan Kehilangan Barang", color=text_color, fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Jumlah Laporan Barang Hilang", color=text_color, fontsize=10)
        ax.tick_params(colors=text_color)
        ax.grid(axis="x", linestyle="--", alpha=0.5, color=grid_color)

        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.1, bar.get_y() + bar.get_height() / 2, f"{int(w)}", va="center", color=text_color, fontweight="bold")

    def _plot_categories(self, ax, stats, text_color, grid_color):
        cats_dict = stats["categories"]
        categories = list(cats_dict.keys())
        lost_vals = [cats_dict[c]["lost"] for c in categories]
        found_vals = [cats_dict[c]["found"] for c in categories]

        import numpy as np
        x = np.arange(len(categories))
        width = 0.35

        ax.bar(x - width/2, lost_vals, width, label="Barang Hilang", color="#EF4444")
        ax.bar(x + width/2, found_vals, width, label="Barang Temuan", color="#10B981")

        ax.set_title("Distribusi Barang Berdasarkan Kategori", color=text_color, fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=15, ha="right", color=text_color, fontsize=9)
        ax.tick_params(colors=text_color)
        ax.grid(axis="y", linestyle="--", alpha=0.5, color=grid_color)
        ax.legend(facecolor=ax.get_facecolor(), edgecolor=grid_color, labelcolor=text_color)

    def _plot_return_rate(self, ax, stats, text_color, bg_color):
        completed = stats["completed_total"]
        active = stats["active_total"]
        total = stats["total_reports"]

        if total == 0:
            ax.text(0.5, 0.5, "Belum ada data status", ha="center", va="center", color=text_color)
            return

        labels = [f"Berhasil Kembali ({completed})", f"Masih Aktif/Proses ({active})"]
        sizes = [completed, active]
        colors = ["#10B981", "#3B82F6"]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops=dict(color=text_color),
            wedgeprops=dict(width=0.45, edgecolor=bg_color, linewidth=2),
        )

        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")

        ax.set_title(f"Tingkat Pengembalian Barang ({stats['return_rate']}%)", color=text_color, fontsize=13, fontweight="bold", pad=12)

    def _plot_time_trend(self, ax, stats, text_color, grid_color):
        hours = stats["hourly_trend"]
        x_labels = list(hours.keys())
        y_vals = list(hours.values())

        ax.plot(x_labels, y_vals, marker="o", color="#3B82F6", linewidth=2.5, markersize=6)
        ax.fill_between(x_labels, y_vals, color="#3B82F6", alpha=0.2)

        ax.set_title("Tren Jam Rawan Kehilangan / Penemuan Barang", color=text_color, fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Waktu Kejadian (Jam)", color=text_color, fontsize=10)
        ax.set_ylabel("Jumlah Laporan", color=text_color, fontsize=10)
        ax.set_xticklabels(x_labels, rotation=35, ha="right", color=text_color, fontsize=8)
        ax.tick_params(colors=text_color)
        ax.grid(True, linestyle="--", alpha=0.5, color=grid_color)
