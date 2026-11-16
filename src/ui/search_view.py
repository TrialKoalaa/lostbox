"""
search_view.py
Halaman Pencarian & Penjelajahan (Search & Browse) seluruh laporan barang di LostBox.
Menyediakan filter multi-kriteria: keyword, tipe, kategori, warna, lantai, dan status.
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import customtkinter as ctk
from tkinter import messagebox

from src.models import Item
from src.ui.dialogs import ItemDetailDialog, MatchReviewDialog


class SearchView(ctk.CTkFrame):
    """
    Halaman pencarian & filter komprehensif untuk seluruh data laporan.
    """

    def __init__(self, parent, data_manager, match_engine, on_update_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.dm = data_manager
        self.engine = match_engine
        self.on_update = on_update_callback

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header_frame,
            text="🔍 Pencarian & Penjelajahan Laporan",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Cari barang berdasarkan kata kunci dan filter spesifik (kategori, warna, lantai, status).",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
        ).pack(anchor="w")

        # 2. Filter Bar Card
        filter_card = ctk.CTkFrame(self, fg_color=("gray92", "gray17"), corner_radius=10)
        filter_card.pack(fill="x", padx=20, pady=(0, 10))

        # Row 1: Search Keyword Entry + Type Selector + Search Button
        r1 = ctk.CTkFrame(filter_card, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=(12, 6))

        self.entry_keyword = ctk.CTkEntry(
            r1,
            placeholder_text="Ketik kata kunci (nama barang, nomor ID, ciri-ciri, nama pelapor)...",
            height=34,
        )
        self.entry_keyword.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_keyword.bind("<Return>", lambda e: self.apply_filter())

        self.var_type = ctk.StringVar(value="Semua Jenis")
        self.opt_type = ctk.CTkOptionMenu(
            r1,
            values=["Semua Jenis", "Barang Hilang", "Barang Temuan"],
            variable=self.var_type,
            width=140,
            command=lambda _: self.apply_filter(),
        )
        self.opt_type.pack(side="left", padx=(0, 10))

        btn_search = ctk.CTkButton(
            r1,
            text="Cari",
            width=90,
            height=34,
            command=self.apply_filter,
            fg_color="#2563EB",
        )
        btn_search.pack(side="left")

        # Row 2: Secondary Filters (Category, Color, Floor, Status, Reset)
        r2 = ctk.CTkFrame(filter_card, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 12))

        # Category
        cats = ["Semua Kategori"] + self.dm.settings.get("categories", [])
        self.var_cat = ctk.StringVar(value=cats[0])
        ctk.CTkOptionMenu(r2, values=cats, variable=self.var_cat, width=150, command=lambda _: self.apply_filter()).pack(side="left", padx=(0, 8))

        # Color
        colors = ["Semua Warna"] + self.dm.settings.get("colors", [])
        self.var_col = ctk.StringVar(value=colors[0])
        ctk.CTkOptionMenu(r2, values=colors, variable=self.var_col, width=130, command=lambda _: self.apply_filter()).pack(side="left", padx=(0, 8))

        # Floor
        self.var_fl = ctk.StringVar(value="Semua Lantai")
        ctk.CTkOptionMenu(r2, values=["Semua Lantai", "Lantai 1", "Lantai 2"], variable=self.var_fl, width=120, command=lambda _: self.apply_filter()).pack(side="left", padx=(0, 8))

        # Status
        statuses = ["Semua Status", "Dilaporkan", "Dicocokkan", "Diklaim", "Selesai"]
        self.var_st = ctk.StringVar(value=statuses[0])
        ctk.CTkOptionMenu(r2, values=statuses, variable=self.var_st, width=130, command=lambda _: self.apply_filter()).pack(side="left", padx=(0, 8))

        # Reset button
        btn_reset = ctk.CTkButton(
            r2,
            text="Reset Filter",
            width=90,
            fg_color=("gray70", "gray40"),
            hover_color=("gray60", "gray50"),
            command=self.reset_filter,
        )
        btn_reset.pack(side="right")

        # 3. Result Count & Summary bar
        summary_row = ctk.CTkFrame(self, fg_color="transparent")
        summary_row.pack(fill="x", padx=20, pady=(0, 6))

        self.lbl_count = ctk.CTkLabel(
            summary_row,
            text="Memuat hasil...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "gray70"),
        )
        self.lbl_count.pack(side="left")

        # 4. Scrollable Container for results
        self.results_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.apply_filter()

    def reset_filter(self):
        self.entry_keyword.delete(0, "end")
        self.var_type.set("Semua Jenis")
        self.var_cat.set("Semua Kategori")
        self.var_col.set("Semua Warna")
        self.var_fl.set("Semua Lantai")
        self.var_st.set("Semua Status")
        self.apply_filter()

    def apply_filter(self):
        for child in self.results_container.winfo_children():
            child.destroy()

        kw = self.entry_keyword.get().strip()
        type_val = self.var_type.get()
        item_type = "ALL"
        if type_val == "Barang Hilang":
            item_type = "LOST"
        elif type_val == "Barang Temuan":
            item_type = "FOUND"

        cat = self.var_cat.get()
        col = self.var_col.get()
        fl_val = self.var_fl.get()
        fl_num = 1 if fl_val == "Lantai 1" else 2 if fl_val == "Lantai 2" else None
        st = self.var_st.get()

        items = self.dm.filter_items(
            item_type=item_type,
            category=cat,
            color=col,
            floor=fl_num,
            status=st,
            keyword=kw,
        )

        total_all = len(self.dm.lost_items) + len(self.dm.found_items)
        self.lbl_count.configure(text=f"Menampilkan {len(items)} dari total {total_all} laporan barang.")

        if not items:
            empty_box = ctk.CTkFrame(self.results_container, fg_color="transparent")
            empty_box.pack(pady=40)
            ctk.CTkLabel(
                empty_box,
                text="Tidak ada laporan yang sesuai dengan kriteria pencarian.",
                font=ctk.CTkFont(size=13),
                text_color="gray50",
            ).pack()
            return

        for item in items:
            self._render_card(item)

    def _render_card(self, item: Item):
        card = ctk.CTkFrame(self.results_container, fg_color=("gray92", "gray19"), corner_radius=8)
        card.pack(fill="x", pady=5, padx=2)

        # Header Row: Badge Type, ID, Date, Status
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(8, 2))

        is_lost = (item.item_type == "LOST")
        type_bg = "#EF4444" if is_lost else "#10B981"
        type_text = "HILANG" if is_lost else "TEMUAN"

        ctk.CTkLabel(
            hdr,
            text=f" {type_text} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=type_bg,
            corner_radius=4,
            text_color="white",
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            hdr,
            text=item.id,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3B82F6",
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            hdr,
            text=f"•  {item.date} {item.time}",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
        ).pack(side="left")

        # Status badge
        stat_colors = {
            "Dilaporkan": "#3B82F6",
            "Dicocokkan": "#F59E0B",
            "Diklaim": "#8B5CF6",
            "Selesai": "#10B981",
            "Kedaluwarsa": "gray50",
        }
        st_color = stat_colors.get(item.status, "#3B82F6")

        ctk.CTkLabel(
            hdr,
            text=f"  {item.status}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=st_color,
            corner_radius=4,
            text_color="white",
        ).pack(side="right")

        # Main Info Row
        mid = ctk.CTkFrame(card, fg_color="transparent")
        mid.pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(
            mid,
            text=item.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            mid,
            text=f"📍 {item.location}",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray75"),
        ).pack(side="right")

        # Details
        desc_text = item.description if item.description else "(Tanpa keterangan)"
        if len(desc_text) > 120:
            desc_text = desc_text[:117] + "..."

        ctk.CTkLabel(
            card,
            text=f"Kategori: {item.category}  |  Warna: {item.color}  |  Pelapor: {item.reporter}\n{desc_text}",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
            anchor="w",
            justify="left",
        ).pack(fill="x", padx=12, pady=(2, 6))

        # Actions Row
        b_bar = ctk.CTkFrame(card, fg_color="transparent")
        b_bar.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkButton(
            b_bar,
            text="Lihat Detail & Status",
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("#2563EB", "#1D4ED8"),
            command=lambda it=item: ItemDetailDialog(self.winfo_toplevel(), it, self.dm, on_update_callback=self.apply_filter),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            b_bar,
            text="🔍 Cari Kecocokan",
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#D97706",
            hover_color="#B45309",
            command=lambda it=item: self._manual_match(it),
        ).pack(side="left")

    def _manual_match(self, item):
        self.engine.set_items(self.dm.lost_items, self.dm.found_items)
        matches = self.engine.find_matches(item, min_score=40.0)
        if matches:
            MatchReviewDialog(
                self.winfo_toplevel(),
                match_data=matches[0],
                data_manager=self.dm,
                on_action_callback=self.apply_filter,
            )
        else:
            messagebox.showinfo("Auto-Matcher", f"Belum ditemukan kecocokan untuk {item.name} ({item.id}).")
