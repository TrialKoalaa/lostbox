"""
dialogs.py
Kumpulan jendela dialog modal untuk LostBox:
- ItemDetailDialog: Melihat rincian lengkap barang dan update status
- MatchReviewDialog: Membandingkan dua barang yang cocok & konfirmasi status
- FloorPickerModal: Memilih ruangan secara visual dari peta untuk form input
"""

import os
import sys

# Tambahkan root direktori projek ke sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from src.models import Item, LostItem, FoundItem, Location


class ItemDetailDialog(ctk.CTkToplevel):
    """
    Dialog untuk melihat rincian barang dan memperbarui lifecycle status.
    """

    def __init__(self, parent, item: Item, data_manager, on_update_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.item = item
        self.dm = data_manager
        self.on_update_callback = on_update_callback

        self.title(f"Detail Barang - {item.id}")
        self.geometry("620x680")
        self.resizable(False, False)

        # Modal focus
        self.grab_set()
        self.attributes("-topmost", True)

        self._build_ui()

    def _build_ui(self):
        # Header banner
        header_color = "#D9534F" if self.item.item_type == "LOST" else "#2ECC71"
        type_text = "BARANG HILANG (LOST)" if self.item.item_type == "LOST" else "BARANG TEMUAN (FOUND)"

        header_frame = ctk.CTkFrame(self, fg_color=header_color, corner_radius=8, height=60)
        header_frame.pack(fill="x", padx=16, pady=(16, 10))
        header_frame.pack_propagate(False)

        title_lbl = ctk.CTkLabel(
            header_frame,
            text=f"{type_text} • {self.item.id}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
        )
        title_lbl.pack(pady=14)

        # Status Lifecycle Breadcrumb Frame
        status_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=8)
        status_frame.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            status_frame,
            text="Lifecycle Status:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(8, 2))

        # Flow indicator
        steps = ["Dilaporkan", "Dicocokkan", "Diklaim", "Selesai"]
        flow_subframe = ctk.CTkFrame(status_frame, fg_color="transparent")
        flow_subframe.pack(fill="x", padx=12, pady=(0, 10))

        current_idx = steps.index(self.item.status) if self.item.status in steps else -1

        for idx, step in enumerate(steps):
            is_active = (idx == current_idx)
            is_past = (idx < current_idx)

            if is_active:
                btn_color = "#3B82F6"
                txt_color = "white"
            elif is_past:
                btn_color = "#10B981"
                txt_color = "white"
            else:
                btn_color = ("gray75", "gray35")
                txt_color = ("gray40", "gray70")

            badge = ctk.CTkButton(
                flow_subframe,
                text=f"{idx+1}. {step}",
                fg_color=btn_color,
                text_color=txt_color,
                font=ctk.CTkFont(size=11, weight="bold" if is_active else "normal"),
                hover=False,
                height=26,
                width=110,
            )
            badge.pack(side="left", padx=3)

        # Details Content Frame (Scrollable)
        content_frame = ctk.CTkScrollableFrame(self, height=360)
        content_frame.pack(fill="both", expand=True, padx=16, pady=8)

        details = [
            ("Nama Barang", self.item.name),
            ("Kategori", self.item.category),
            ("Warna Dominan", self.item.color),
            ("Lokasi", str(self.item.location)),
            ("Tanggal & Waktu", f"{self.item.date} pukul {self.item.time or '-'}"),
            ("Pelapor", self.item.reporter),
        ]

        if isinstance(self.item, FoundItem):
            details.append(("Status Penyimpanan", self.item.kept_at))

        details.append(("Deskripsi / Ciri", self.item.description or "(Tidak ada deskripsi tambahan)"))

        for label, val in details:
            row_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=4)

            ctk.CTkLabel(
                row_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=150,
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                row_frame,
                text=val,
                font=ctk.CTkFont(size=12),
                anchor="w",
                wraplength=380,
                justify="left",
            ).pack(side="left", fill="x", expand=True)

        # Action Buttons & Status Changer
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=16, pady=(6, 16))

        # Status Update Dropdown
        ctk.CTkLabel(bottom_frame, text="Ubah Status:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))

        self.status_var = ctk.StringVar(value=self.item.status)
        status_dropdown = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Dilaporkan", "Dicocokkan", "Diklaim", "Selesai", "Kedaluwarsa"],
            variable=self.status_var,
            width=140,
        )
        status_dropdown.pack(side="left", padx=(0, 8))

        btn_apply = ctk.CTkButton(
            bottom_frame,
            text="Simpan Status",
            command=self._apply_status_change,
            width=110,
            fg_color="#2563EB",
        )
        btn_apply.pack(side="left", padx=(0, 10))

        btn_close = ctk.CTkButton(
            bottom_frame,
            text="Tutup",
            command=self.destroy,
            width=90,
            fg_color=("gray70", "gray40"),
            hover_color=("gray60", "gray50"),
        )
        btn_close.pack(side="right")

    def _apply_status_change(self):
        new_status = self.status_var.get()
        self.dm.update_item_status(self.item.id, new_status)
        if self.on_update_callback:
            self.on_update_callback()
        self.destroy()


class MatchReviewDialog(ctk.CTkToplevel):
    """
    Dialog peninjauan hasil pencocokan (Lost vs Found).
    Memungkinkan pengguna melihat perbandingan dan mengambil keputusan
    (Konfirmasi Cocok, Bukan Barang yang Sama, Klaim, Selesai).
    """

    def __init__(self, parent, match_data: Dict[str, Any], data_manager, on_action_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.match_data = match_data
        self.dm = data_manager
        self.on_action_callback = on_action_callback

        self.target_item: Item = match_data["target_item"]
        self.candidate_item: Item = match_data["candidate_item"]
        self.score: float = match_data["score"]
        self.reasons = match_data.get("reasons", [])

        self.title("Peninjauan Kecocokan Barang")
        self.geometry("740x660")
        self.resizable(False, False)

        self.grab_set()
        self.attributes("-topmost", True)

        self._build_ui()

    def _build_ui(self):
        # Header with score
        header_frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=8)
        header_frame.pack(fill="x", padx=16, pady=(16, 10))

        # Star rating display
        stars = "★★★★★" if self.score >= 90 else "★★★★☆" if self.score >= 75 else "★★★☆☆" if self.score >= 60 else "★★☆☆☆"

        score_lbl = ctk.CTkLabel(
            header_frame,
            text=f"🔔 Skor Kecocokan: {self.score}% ({stars})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FBBF24" if self.score >= 70 else "#60A5FA",
        )
        score_lbl.pack(pady=(12, 4))

        sub_lbl = ctk.CTkLabel(
            header_frame,
            text="Sistem mendeteksi indikasi kuat barang yang sama berdasarkan atribut di bawah ini.",
            font=ctk.CTkFont(size=12),
            text_color="#CBD5E1",
        )
        sub_lbl.pack(pady=(0, 12))

        # Reasons list
        if self.reasons:
            reasons_frame = ctk.CTkFrame(self, fg_color=("gray92", "gray22"), corner_radius=6)
            reasons_frame.pack(fill="x", padx=16, pady=4)
            reasons_text = " • " + "   • ".join(self.reasons)
            ctk.CTkLabel(
                reasons_frame,
                text=reasons_text,
                font=ctk.CTkFont(size=11),
                text_color=("gray20", "gray85"),
                wraplength=700,
                justify="center",
            ).pack(padx=10, pady=8)

        # Comparison 2-Columns Box
        comp_frame = ctk.CTkFrame(self, fg_color="transparent")
        comp_frame.pack(fill="both", expand=True, padx=16, pady=10)

        # Determine which is lost and which is found
        lost = self.target_item if isinstance(self.target_item, LostItem) else self.candidate_item
        found = self.candidate_item if isinstance(self.target_item, LostItem) else self.target_item

        # Left Column: Lost Item
        lost_box = ctk.CTkFrame(comp_frame, fg_color=("gray95", "gray17"), corner_radius=8, border_width=1, border_color="#EF4444")
        lost_box.pack(side="left", fill="both", expand=True, padx=(0, 6))

        lost_hdr = ctk.CTkLabel(
            lost_box,
            text=f"🔴 LAPORAN KEHILANGAN\n({lost.id})",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#DC2626",
        )
        lost_hdr.pack(pady=(10, 8))

        self._render_item_card_details(lost_box, lost)

        # Right Column: Found Item
        found_box = ctk.CTkFrame(comp_frame, fg_color=("gray95", "gray17"), corner_radius=8, border_width=1, border_color="#10B981")
        found_box.pack(side="right", fill="both", expand=True, padx=(6, 0))

        found_hdr = ctk.CTkLabel(
            found_box,
            text=f"🟢 LAPORAN TEMUAN\n({found.id})",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#059669",
        )
        found_hdr.pack(pady=(10, 8))

        self._render_item_card_details(found_box, found)

        # Bottom Action Buttons
        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(8, 16))

        btn_confirm = ctk.CTkButton(
            btn_bar,
            text="✔ Konfirmasi Cocok (Tandai Dicocokkan)",
            command=lambda: self._handle_action("Dicocokkan", lost.id, found.id),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=34,
        )
        btn_confirm.pack(side="left", padx=(0, 6))

        btn_claim = ctk.CTkButton(
            btn_bar,
            text="📌 Verifikasi Klaim",
            command=lambda: self._handle_action("Diklaim", lost.id, found.id),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            height=34,
        )
        btn_claim.pack(side="left", padx=4)

        btn_complete = ctk.CTkButton(
            btn_bar,
            text="🎉 Selesai Dikembalikan",
            command=lambda: self._handle_action("Selesai", lost.id, found.id),
            fg_color="#10B981",
            hover_color="#059669",
            height=34,
        )
        btn_complete.pack(side="left", padx=4)

        btn_reject = ctk.CTkButton(
            btn_bar,
            text="✖ Bukan Barang yang Sama",
            command=lambda: self._handle_action("Bukan barang yang sama", lost.id, found.id),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            height=34,
            width=160,
        )
        btn_reject.pack(side="right")

    def _render_item_card_details(self, parent_box, item: Item):
        items_data = [
            ("Nama", item.name),
            ("Kategori", item.category),
            ("Warna", item.color),
            ("Lokasi", str(item.location)),
            ("Tanggal", item.date),
            ("Waktu", item.time or "-"),
            ("Pelapor", item.reporter),
        ]
        if isinstance(item, FoundItem):
            items_data.append(("Penyimpanan", item.kept_at))

        items_data.append(("Ciri", item.description or "-"))

        for label, val in items_data:
            row = ctk.CTkFrame(parent_box, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=11, weight="bold"), width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=11), anchor="w", wraplength=210, justify="left").pack(side="left", fill="x", expand=True)

    def _handle_action(self, action: str, lost_id: str, found_id: str):
        if action == "Dicocokkan":
            self.dm.record_match(lost_id, found_id, self.score)
        elif action in ("Diklaim", "Selesai"):
            self.dm.update_item_status(lost_id, action)
            self.dm.update_item_status(found_id, action)
        elif action == "Bukan barang yang sama":
            self.dm.update_item_status(lost_id, "Dilaporkan")
            self.dm.update_item_status(found_id, "Dilaporkan")

        if self.on_action_callback:
            self.on_action_callback()
        self.destroy()


class FloorPickerModal(ctk.CTkToplevel):
    """
    Modal peta mini interaktif untuk memilih ruangan langsung dari gambar denah.
    Saat sebuah ruangan diklik, otomatis mengirimkan pilihan ruangan ke form pelaporan.
    """

    def __init__(self, parent, initial_floor: int = 1, on_select_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.initial_floor = initial_floor
        self.on_select_callback = on_select_callback

        self.title("Pilih Lokasi dari Peta Lantai")
        self.geometry("640x520")
        self.resizable(False, False)

        self.grab_set()
        self.attributes("-topmost", True)

        self.current_floor = initial_floor
        self._build_ui()

    def _build_ui(self):
        # Header
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            top_bar,
            text="Klik salah satu ruangan di bawah untuk memilih lokasi:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left")

        # Floor switch tab
        self.floor_seg = ctk.CTkSegmentedButton(
            top_bar,
            values=["Lantai 1", "Lantai 2"],
            command=self._on_floor_tab_change,
        )
        self.floor_seg.set(f"Lantai {self.current_floor}")
        self.floor_seg.pack(side="right")

        # Grid container
        self.grid_container = ctk.CTkFrame(self, fg_color=("gray90", "gray17"), corner_radius=10)
        self.grid_container.pack(fill="both", expand=True, padx=16, pady=8)

        self._render_rooms()

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkButton(
            footer,
            text="Batal",
            command=self.destroy,
            width=90,
            fg_color=("gray70", "gray40"),
        ).pack(side="right")

    def _on_floor_tab_change(self, val):
        self.current_floor = 1 if "1" in val else 2
        self._render_rooms()

    def _render_rooms(self):
        # Clear existing
        for child in self.grid_container.winfo_children():
            child.destroy()

        # Room data based on PDF page 3
        if self.current_floor == 1:
            rooms = [
                {"code": "LOBBY", "name": "LOBBY / HALL", "row": 0, "col": 0, "colspan": 3},
                {"code": "R101", "name": "Ruang Kuliah 101", "row": 1, "col": 0, "colspan": 1},
                {"code": "R102", "name": "Ruang Kuliah 102", "row": 1, "col": 1, "colspan": 1},
                {"code": "DOSEN", "name": "Ruang Dosen", "row": 1, "col": 2, "colspan": 1},
                {"code": "TOILET_L1", "name": "Toilet L1", "row": 2, "col": 0, "colspan": 1},
                {"code": "TANGGA_L1", "name": "Tangga", "row": 2, "col": 1, "colspan": 1},
                {"code": "TU", "name": "TU / Admin", "row": 2, "col": 2, "colspan": 1},
                {"code": "TERAS", "name": "AREA PARKIR / TERAS DEPAN", "row": 3, "col": 0, "colspan": 3},
            ]
        else:
            rooms = [
                {"code": "KORIDOR", "name": "KORIDOR ATAS", "row": 0, "col": 0, "colspan": 3},
                {"code": "LAB201", "name": "Lab Komputer 201", "row": 1, "col": 0, "colspan": 1},
                {"code": "LAB202", "name": "Lab Data 202", "row": 1, "col": 1, "colspan": 1},
                {"code": "R203", "name": "Ruang Kuliah 203", "row": 1, "col": 2, "colspan": 1},
                {"code": "TOILET_L2", "name": "Toilet L2", "row": 2, "col": 0, "colspan": 1},
                {"code": "TANGGA_L2", "name": "Tangga", "row": 2, "col": 1, "colspan": 1},
                {"code": "SEMINAR", "name": "Ruang Seminar", "row": 2, "col": 2, "colspan": 1},
                {"code": "MUSHOLLA", "name": "MUSHOLLA / RUANG MAHASISWA", "row": 3, "col": 0, "colspan": 3},
            ]

        # Configure 3 columns
        for c in range(3):
            self.grid_container.grid_columnconfigure(c, weight=1)
        for r in range(4):
            self.grid_container.grid_rowconfigure(r, weight=1)

        for room in rooms:
            btn = ctk.CTkButton(
                self.grid_container,
                text=f"{room['name']}\n({room['code']})",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("#3B82F6", "#1E3A8A"),
                hover_color=("#2563EB", "#1D4ED8"),
                height=70,
                command=lambda r=room: self._select_room(r),
            )
            btn.grid(
                row=room["row"],
                column=room["col"],
                columnspan=room.get("colspan", 1),
                padx=8,
                pady=8,
                sticky="nsew",
            )

    def _select_room(self, room):
        if self.on_select_callback:
            loc = Location(floor=self.current_floor, room_name=room["name"], room_code=room["code"])
            self.on_select_callback(loc)
        self.destroy()
