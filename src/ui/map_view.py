"""
map_view.py
Tampilan Peta Lantai Gedung Interaktif (Floor Plan)
Menerapkan konsep CustomTkinter Frame Grid, Event Handling, dan dynamic styling.
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import customtkinter as ctk
from typing import Dict, Any, Optional, List
from src.models import Item, LostItem, FoundItem
from src.ui.dialogs import ItemDetailDialog


class MapView(ctk.CTkFrame):
    """
    Halaman Denah / Peta Lantai Gedung Prodi Sains Data Interaktif.
    """

    def __init__(self, parent, data_manager, match_engine, on_navigate_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.dm = data_manager
        self.engine = match_engine
        self.on_navigate = on_navigate_callback

        self.current_floor = 1
        self.selected_room = None
        self.room_buttons: Dict[str, ctk.CTkButton] = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Top Controls & Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="🗺️ Peta Interaktif Gedung Prodi",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Pilih lantai dan klik kotak ruangan untuk melihat daftar laporan aktif di lokasi tersebut.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
        ).pack(anchor="w")

        # Floor switch tab
        self.floor_seg = ctk.CTkSegmentedButton(
            header_frame,
            values=["Lantai 1", "Lantai 2"],
            command=self._on_floor_change,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            width=220,
        )
        self.floor_seg.set("Lantai 1")
        self.floor_seg.pack(side="right", padx=4)

        # 2. Main Content Split (Left: Map Grid, Right: Room Detail Panel)
        main_body = ctk.CTkFrame(self, fg_color="transparent")
        main_body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Left: Map Container
        map_outer = ctk.CTkFrame(main_body, fg_color=("gray92", "gray17"), corner_radius=10)
        map_outer.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Floor Label Banner
        self.floor_banner = ctk.CTkLabel(
            map_outer,
            text="DENAH LANTAI 1",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3B82F6",
        )
        self.floor_banner.pack(pady=(12, 6))

        # Grid of Rooms
        self.grid_frame = ctk.CTkFrame(map_outer, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=14, pady=8)

        # Legend / Keterangan
        legend_frame = ctk.CTkFrame(map_outer, fg_color="transparent")
        legend_frame.pack(fill="x", padx=14, pady=(4, 12))

        ctk.CTkLabel(
            legend_frame,
            text="Keterangan:  🔴 Ada Barang Hilang   🟢 Ada Barang Temuan   🟠 Keduanya   ⚪ Kosong",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
        ).pack(side="left")

        # Right: Detail Panel for selected room
        self.detail_panel = ctk.CTkFrame(main_body, width=320, fg_color=("gray95", "gray18"), corner_radius=10)
        self.detail_panel.pack(side="right", fill="both", padx=(0, 0))
        self.detail_panel.pack_propagate(False)

        self._build_detail_panel()
        self.refresh_map()

    def _build_detail_panel(self):
        for child in self.detail_panel.winfo_children():
            child.destroy()

        # Title
        self.panel_title = ctk.CTkLabel(
            self.detail_panel,
            text="Detail Ruangan",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.panel_title.pack(anchor="w", padx=14, pady=(14, 4))

        self.panel_sub = ctk.CTkLabel(
            self.detail_panel,
            text="Klik ruangan di peta untuk melihat barang.",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
        )
        self.panel_sub.pack(anchor="w", padx=14, pady=(0, 10))

        # Scrollable list for room items
        self.room_items_list = ctk.CTkScrollableFrame(self.detail_panel, fg_color="transparent")
        self.room_items_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_floor_change(self, val):
        self.current_floor = 1 if "1" in val else 2
        self.floor_banner.configure(text=f"DENAH LANTAI {self.current_floor}")
        self.selected_room = None
        self.refresh_map()

    def refresh_map(self):
        """Merender ulang peta berdasarkan data terbaru di DataManager."""
        for child in self.grid_frame.winfo_children():
            child.destroy()

        self.room_buttons.clear()
        room_counts = self.dm.get_room_item_counts()

        # Grid config: 3 columns, 4 rows
        for c in range(3):
            self.grid_frame.grid_columnconfigure(c, weight=1)
        for r in range(4):
            self.grid_frame.grid_rowconfigure(r, weight=1)

        rooms = self.dm.settings.get("floors", {}).get(str(self.current_floor), [])

        for room in rooms:
            code = room["code"]
            name = room["name"]
            counts = room_counts.get(code, {"lost": 0, "found": 0, "total": 0})
            total = counts["total"]
            lost_c = counts["lost"]
            found_c = counts["found"]

            # Dynamic button styling
            if lost_c > 0 and found_c > 0:
                fg_col = "#D97706"  # Amber
                hover_col = "#B45309"
                badge_str = f"🔴 {lost_c}  🟢 {found_c}"
            elif lost_c > 0:
                fg_col = "#DC2626"  # Red
                hover_col = "#B91C1C"
                badge_str = f"🔴 {lost_c} Hilang"
            elif found_c > 0:
                fg_col = "#059669"  # Green
                hover_col = "#047857"
                badge_str = f"🟢 {found_c} Temuan"
            else:
                fg_col = ("#475569", "#334155")  # Neutral slate
                hover_col = ("#334155", "#1E293B")
                badge_str = "(0)"

            btn_text = f"{name}\n({code})\n{badge_str}"

            # If selected, show border highlight
            border_w = 2 if self.selected_room and self.selected_room["code"] == code else 0
            border_c = "#FBBF24"

            btn = ctk.CTkButton(
                self.grid_frame,
                text=btn_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=fg_col,
                hover_color=hover_col,
                border_width=border_w,
                border_color=border_c,
                height=80,
                command=lambda r=room: self._on_room_click(r),
            )
            btn.grid(
                row=room["row"],
                column=room["col"],
                columnspan=room.get("colspan", 1),
                padx=6,
                pady=6,
                sticky="nsew",
            )
            self.room_buttons[code] = btn

        # Jika ada ruangan terpilih, update detail panel
        if self.selected_room:
            self._render_selected_room_items()
        else:
            self._clear_detail_panel()

    def _on_room_click(self, room):
        self.selected_room = room
        # Re-render borders
        for code, btn in self.room_buttons.items():
            if code == room["code"]:
                btn.configure(border_width=3, border_color="#FBBF24")
            else:
                btn.configure(border_width=0)

        self._render_selected_room_items()

    def _clear_detail_panel(self):
        for child in self.room_items_list.winfo_children():
            child.destroy()
        self.panel_title.configure(text="Pilih Ruangan")
        self.panel_sub.configure(text="Klik salah satu kotak ruangan di denah.")

        empty_lbl = ctk.CTkLabel(
            self.room_items_list,
            text="Belum ada ruangan yang dipilih.\nKlik salah satu ruangan di peta.",
            font=ctk.CTkFont(size=12),
            text_color="gray50",
            justify="center",
        )
        empty_lbl.pack(pady=40)

    def _render_selected_room_items(self):
        for child in self.room_items_list.winfo_children():
            child.destroy()

        room_name = self.selected_room["name"]
        room_code = self.selected_room["code"]

        self.panel_title.configure(text=f"📍 {room_name}")
        self.panel_sub.configure(text=f"Kode: {room_code} • Lantai {self.current_floor}")

        # Get items for this room
        items = self.dm.filter_items(
            item_type="ALL",
            floor=self.current_floor,
            room_code=room_code,
        )

        # Hanya ambil laporan aktif
        active_items = [i for i in items if i.status in ("Dilaporkan", "Dicocokkan", "Diklaim")]

        if not active_items:
            empty_frame = ctk.CTkFrame(self.room_items_list, fg_color="transparent")
            empty_frame.pack(fill="x", pady=30)
            ctk.CTkLabel(
                empty_frame,
                text="✔ Tidak ada laporan aktif\ndi ruangan ini saat ini.",
                font=ctk.CTkFont(size=12),
                text_color="gray50",
            ).pack()
            return

        for item in active_items:
            card = ctk.CTkFrame(self.room_items_list, fg_color=("gray90", "gray22"), corner_radius=6)
            card.pack(fill="x", pady=4, padx=2)

            is_lost = (item.item_type == "LOST")
            badge_col = "#EF4444" if is_lost else "#10B981"
            type_txt = "HILANG" if is_lost else "TEMUAN"

            # Top row
            top_r = ctk.CTkFrame(card, fg_color="transparent")
            top_r.pack(fill="x", padx=8, pady=(6, 2))

            ctk.CTkLabel(
                top_r,
                text=type_txt,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=badge_col,
            ).pack(side="left")

            ctk.CTkLabel(
                top_r,
                text=item.date,
                font=ctk.CTkFont(size=10),
                text_color=("gray40", "gray70"),
            ).pack(side="right")

            # Name
            ctk.CTkLabel(
                card,
                text=item.name,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            ).pack(fill="x", padx=8, pady=1)

            # Reporter & Category
            ctk.CTkLabel(
                card,
                text=f"{item.category} • {item.color}\nOleh: {item.reporter}",
                font=ctk.CTkFont(size=10),
                text_color=("gray30", "gray75"),
                anchor="w",
                justify="left",
            ).pack(fill="x", padx=8, pady=1)

            # Detail button
            btn_dtl = ctk.CTkButton(
                card,
                text="Lihat Detail",
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=("#3B82F6", "#2563EB"),
                command=lambda it=item: self._open_detail_dialog(it),
            )
            btn_dtl.pack(fill="x", padx=8, pady=(4, 6))

    def _open_detail_dialog(self, item: Item):
        ItemDetailDialog(self.winfo_toplevel(), item, self.dm, on_update_callback=self.refresh_map)
