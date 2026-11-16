"""
report_view.py
Halaman Formulir Pelaporan Barang Hilang & Barang Temuan.
Dilengkapi integrasi otomatis ke Auto-Matcher dan FloorPickerModal.
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from src.models import Location, LostItem, FoundItem
from src.data_manager import ValidationError
from src.ui.dialogs import FloorPickerModal, MatchReviewDialog, ItemDetailDialog


class ReportView(ctk.CTkFrame):
    """
    Halaman form input pelaporan barang (Lost / Found) beserta daftar item.
    """

    def __init__(self, parent, data_manager, match_engine, report_type="LOST", on_change_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.dm = data_manager
        self.engine = match_engine
        self.report_type = report_type.upper()  # "LOST" or "FOUND"
        self.on_change = on_change_callback

        self.selected_location: Location = Location(1, "Lobby / Hall", "LOBBY")

        self._build_ui()

    def _build_ui(self):
        # 1. Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        is_lost = (self.report_type == "LOST")
        title_text = "📝 Lapor Barang Hilang" if is_lost else "📦 Lapor Barang Temuan"
        desc_text = (
            "Isi formulir berikut jika Anda kehilangan barang di lingkungan Gedung Prodi Sains Data."
            if is_lost
            else "Isi formulir berikut jika Anda menemukan barang di lingkungan Gedung Prodi Sains Data."
        )

        ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#EF4444" if is_lost else "#10B981",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
        ).pack(anchor="w")

        # 2. Tabview: [ Formulir Input ] dan [ Daftar Laporan ]
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        tab_form_name = "Formulir Lapor"
        tab_list_name = f"Daftar Barang ({'Hilang' if is_lost else 'Temuan'})"
        self.tabview.add(tab_form_name)
        self.tabview.add(tab_list_name)

        self._build_form_tab(self.tabview.tab(tab_form_name))
        self._build_list_tab(self.tabview.tab(tab_list_name))

    def _build_form_tab(self, parent_tab):
        scroll_form = ctk.CTkScrollableFrame(parent_tab, fg_color="transparent")
        scroll_form.pack(fill="both", expand=True, padx=10, pady=10)

        # Container Box
        form_card = ctk.CTkFrame(scroll_form, fg_color=("gray92", "gray17"), corner_radius=10)
        form_card.pack(fill="x", padx=10, pady=5)

        # 1. Nama Pelapor
        row1 = ctk.CTkFrame(form_card, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row1, text="Nama Pelapor *:", font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")
        self.entry_reporter = ctk.CTkEntry(row1, placeholder_text="Contoh: Ahmad Rizky / Pak Supri")
        self.entry_reporter.pack(side="left", fill="x", expand=True)

        # 2. Nama Barang
        row2 = ctk.CTkFrame(form_card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row2, text="Nama Barang *:", font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")
        self.entry_name = ctk.CTkEntry(row2, placeholder_text="Contoh: Charger Laptop Asus / Botol Corkcicle")
        self.entry_name.pack(side="left", fill="x", expand=True)

        # 3. Kategori Barang
        categories = self.dm.settings.get("categories", [
            "Elektronik", "Pakaian / Aksesoris", "Alat Tulis", "Botol / Tumbler", "Tas / Dompet", "Lainnya"
        ])
        row3 = ctk.CTkFrame(form_card, fg_color="transparent")
        row3.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row3, text="Kategori Barang *:", font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")
        self.var_category = ctk.StringVar(value=categories[0])
        self.opt_category = ctk.CTkOptionMenu(row3, values=categories, variable=self.var_category)
        self.opt_category.pack(side="left", fill="x", expand=True)

        # 4. Warna Dominan
        colors = self.dm.settings.get("colors", [
            "Hitam", "Putih", "Abu-abu", "Biru", "Merah", "Hijau", "Kuning", "Cokelat", "Pink", "Oranye", "Lainnya"
        ])
        row4 = ctk.CTkFrame(form_card, fg_color="transparent")
        row4.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row4, text="Warna Dominan *:", font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")
        self.var_color = ctk.StringVar(value=colors[0])
        self.opt_color = ctk.CTkOptionMenu(row4, values=colors, variable=self.var_color)
        self.opt_color.pack(side="left", fill="x", expand=True)

        # 5. Lokasi (Lantai + Ruangan + Tombol Peta)
        row5 = ctk.CTkFrame(form_card, fg_color="transparent")
        row5.pack(fill="x", padx=16, pady=8)
        loc_label = "Lokasi Terakhir Terlihat *:" if self.report_type == "LOST" else "Lokasi Ditemukan *:"
        ctk.CTkLabel(row5, text=loc_label, font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")

        # Floor selector
        self.var_floor = ctk.StringVar(value="Lantai 1")
        self.opt_floor = ctk.CTkOptionMenu(
            row5,
            values=["Lantai 1", "Lantai 2"],
            variable=self.var_floor,
            width=110,
            command=self._on_floor_selected,
        )
        self.opt_floor.pack(side="left", padx=(0, 8))

        # Room selector
        self.var_room = ctk.StringVar()
        self.opt_room = ctk.CTkOptionMenu(row5, values=["Memuat..."], variable=self.var_room, width=200, command=self._on_room_selected)
        self.opt_room.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Button Open Map Modal
        btn_map_pick = ctk.CTkButton(
            row5,
            text="🗺️ Buka Peta",
            width=100,
            fg_color="#3B82F6",
            command=self._open_floor_picker,
        )
        btn_map_pick.pack(side="left")

        # 6. Tanggal & Waktu
        now = datetime.now()
        row6 = ctk.CTkFrame(form_card, fg_color="transparent")
        row6.pack(fill="x", padx=16, pady=8)
        date_lbl = "Tanggal Kejadian *:" if self.report_type == "LOST" else "Tanggal Ditemukan *:"
        ctk.CTkLabel(row6, text=date_lbl, font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")

        self.entry_date = ctk.CTkEntry(row6, placeholder_text="YYYY-MM-DD", width=140)
        self.entry_date.insert(0, now.strftime("%Y-%m-%d"))
        self.entry_date.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(row6, text="Perkiraan Waktu (HH:MM):", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        self.entry_time = ctk.CTkEntry(row6, placeholder_text="HH:MM", width=100)
        self.entry_time.insert(0, now.strftime("%H:%M"))
        self.entry_time.pack(side="left")

        # 7. Status Penyimpanan (Khusus FoundItem)
        if self.report_type == "FOUND":
            kept_options = self.dm.settings.get("kept_at_options", [
                "Dititipkan ke TU", "Dibawa pelapor", "Ditaruh di lokasi"
            ])
            row7 = ctk.CTkFrame(form_card, fg_color="transparent")
            row7.pack(fill="x", padx=16, pady=8)
            ctk.CTkLabel(row7, text="Status Penyimpanan *:", font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="w").pack(side="left")
            self.var_kept_at = ctk.StringVar(value=kept_options[0])
            self.opt_kept_at = ctk.CTkOptionMenu(row7, values=kept_options, variable=self.var_kept_at)
            self.opt_kept_at.pack(side="left", fill="x", expand=True)

        # 8. Deskripsi Tambahan
        row8 = ctk.CTkFrame(form_card, fg_color="transparent")
        row8.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row8, text="Deskripsi & Ciri Khusus:", font=ctk.CTkFont(size=12, weight="bold"), width=160, anchor="nw").pack(side="left")
        self.txt_desc = ctk.CTkTextbox(row8, height=80)
        self.txt_desc.pack(side="left", fill="x", expand=True)

        # Buttons Bar: Reset & Submit
        btn_bar = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(12, 16))

        btn_reset = ctk.CTkButton(
            btn_bar,
            text="❌ Reset Form",
            fg_color=("gray70", "gray40"),
            hover_color=("gray60", "gray50"),
            width=120,
            command=self._reset_form,
        )
        btn_reset.pack(side="left")

        submit_color = "#DC2626" if self.report_type == "LOST" else "#059669"
        btn_submit = ctk.CTkButton(
            btn_bar,
            text="📤 Kirim Laporan Sekarang",
            fg_color=submit_color,
            hover_color="#B91C1C" if self.report_type == "LOST" else "#047857",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            command=self._submit_report,
        )
        btn_submit.pack(side="right")

        # Initial populate of room dropdown
        self._populate_room_options(1)

    def _populate_room_options(self, floor_num: int):
        rooms = self.dm.get_room_list(floor=floor_num)
        room_names = [f"{r['name']} ({r['code']})" for r in rooms]
        self.opt_room.configure(values=room_names)
        if room_names:
            self.var_room.set(room_names[0])
            self._update_selected_location_from_name(room_names[0], floor_num)

    def _on_floor_selected(self, val):
        fl_num = 1 if "1" in val else 2
        self._populate_room_options(fl_num)

    def _on_room_selected(self, val):
        fl_num = 1 if "1" in self.var_floor.get() else 2
        self._update_selected_location_from_name(val, fl_num)

    def _update_selected_location_from_name(self, formatted_name: str, floor_num: int):
        # Format: Name (CODE)
        import re
        m = re.search(r"^(.*?)\s*\((.*?)\)$", formatted_name)
        if m:
            r_name = m.group(1).strip()
            r_code = m.group(2).strip()
            self.selected_location = Location(floor=floor_num, room_name=r_name, room_code=r_code)

    def _open_floor_picker(self):
        fl_num = 1 if "1" in self.var_floor.get() else 2
        FloorPickerModal(self.winfo_toplevel(), initial_floor=fl_num, on_select_callback=self._handle_picker_selection)

    def _handle_picker_selection(self, loc: Location):
        self.selected_location = loc
        self.var_floor.set(f"Lantai {loc.floor}")
        self._populate_room_options(loc.floor)
        self.var_room.set(f"{loc.room_name} ({loc.room_code})")

    def _reset_form(self):
        self.entry_reporter.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.txt_desc.delete("1.0", "end")
        now = datetime.now()
        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, now.strftime("%Y-%m-%d"))
        self.entry_time.delete(0, "end")
        self.entry_time.insert(0, now.strftime("%H:%M"))

    def _submit_report(self):
        data = {
            "reporter": self.entry_reporter.get().strip(),
            "name": self.entry_name.get().strip(),
            "category": self.var_category.get(),
            "color": self.var_color.get(),
            "location": self.selected_location.to_dict(),
            "date": self.entry_date.get().strip(),
            "time": self.entry_time.get().strip(),
            "description": self.txt_desc.get("1.0", "end").strip(),
            "status": "Dilaporkan",
        }

        if self.report_type == "FOUND":
            data["kept_at"] = self.var_kept_at.get()

        try:
            # 1. Save data via DataManager (validates automatically)
            if self.report_type == "LOST":
                new_item = self.dm.add_lost_item(data)
            else:
                new_item = self.dm.add_found_item(data)

            # 2. Trigger Auto Matcher!
            self.engine.set_items(self.dm.lost_items, self.dm.found_items)
            matches = self.engine.find_matches(new_item, min_score=40.0)

            # 3. Refresh list and reset form
            self._reset_form()
            self._refresh_list_tab()
            if self.on_change:
                self.on_change()

            # 4. If match found, show popup dialog
            if matches:
                top_match = matches[0]
                messagebox.showinfo(
                    "LostBox Auto-Matcher",
                    f"🎉 Kemungkinan Cocok Ditemukan!\n"
                    f"Skor: {top_match['score']}%\n"
                    f"Kandidat: {top_match['candidate_item'].name} ({top_match['candidate_id']})\n\n"
                    "Membuka dialog tinjauan kecocokan..."
                )
                MatchReviewDialog(
                    self.winfo_toplevel(),
                    match_data=top_match,
                    data_manager=self.dm,
                    on_action_callback=self._on_match_action_completed
                )
            else:
                messagebox.showinfo(
                    "Laporan Berhasil",
                    f"Laporan {new_item.id} berhasil disimpan!\nSaat ini belum ditemukan kecocokan langsung. "
                    "Sistem akan otomatis mencocokkan jika ada laporan baru yang sesuai."
                )

        except ValidationError as ve:
            messagebox.showerror("Validasi Gagal", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def _on_match_action_completed(self):
        self._refresh_list_tab()
        if self.on_change:
            self.on_change()

    # ==========================================
    # TAB: LIST OF ITEMS
    # ==========================================
    def _build_list_tab(self, parent_tab):
        top_bar = ctk.CTkFrame(parent_tab, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(top_bar, text="Filter Status:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))

        self.list_status_filter = ctk.StringVar(value="Semua Status")
        ctk.CTkOptionMenu(
            top_bar,
            values=["Semua Status", "Dilaporkan", "Dicocokkan", "Diklaim", "Selesai"],
            variable=self.list_status_filter,
            command=lambda _: self._refresh_list_tab(),
            width=140,
        ).pack(side="left", padx=(0, 10))

        btn_reload = ctk.CTkButton(
            top_bar,
            text="🔄 Segarkan Data",
            command=self._refresh_list_tab,
            width=110,
        )
        btn_reload.pack(side="right")

        # Scrollable items container
        self.list_container = ctk.CTkScrollableFrame(parent_tab, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._refresh_list_tab()

    def _refresh_list_tab(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        status_filt = self.list_status_filter.get()
        items = self.dm.filter_items(
            item_type=self.report_type,
            status=status_filt if status_filt != "Semua Status" else None,
        )

        if not items:
            ctk.CTkLabel(
                self.list_container,
                text="Belum ada data laporan yang sesuai filter.",
                font=ctk.CTkFont(size=13),
                text_color="gray50",
            ).pack(pady=40)
            return

        for item in items:
            self._render_item_card(item)

    def _render_item_card(self, item):
        card = ctk.CTkFrame(self.list_container, fg_color=("gray92", "gray19"), corner_radius=8)
        card.pack(fill="x", pady=5, padx=2)

        # Top row: ID, Date, Status badge
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(8, 2))

        ctk.CTkLabel(top_row, text=item.id, font=ctk.CTkFont(size=12, weight="bold"), text_color="#3B82F6").pack(side="left")
        ctk.CTkLabel(top_row, text=f"•  {item.date} {item.time}", font=ctk.CTkFont(size=11), text_color=("gray40", "gray70")).pack(side="left", padx=8)

        # Status badge color
        stat_colors = {
            "Dilaporkan": "#3B82F6",
            "Dicocokkan": "#F59E0B",
            "Diklaim": "#8B5CF6",
            "Selesai": "#10B981",
            "Kedaluwarsa": "gray50",
        }
        st_color = stat_colors.get(item.status, "#3B82F6")

        ctk.CTkLabel(
            top_row,
            text=f"  {item.status}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=st_color,
            corner_radius=4,
            text_color="white",
        ).pack(side="right")

        # Name & Location
        mid_row = ctk.CTkFrame(card, fg_color="transparent")
        mid_row.pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(mid_row, text=item.name, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(mid_row, text=f"📍 {item.location}", font=ctk.CTkFont(size=11), text_color=("gray30", "gray75")).pack(side="right")

        # Details
        desc_preview = item.description if item.description else "(Tanpa keterangan tambahan)"
        if len(desc_preview) > 90:
            desc_preview = desc_preview[:87] + "..."

        ctk.CTkLabel(
            card,
            text=f"Kategori: {item.category}  |  Warna: {item.color}  |  Pelapor: {item.reporter}\n{desc_preview}",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray70"),
            anchor="w",
            justify="left",
        ).pack(fill="x", padx=12, pady=(2, 6))

        # Bottom actions
        b_bar = ctk.CTkFrame(card, fg_color="transparent")
        b_bar.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkButton(
            b_bar,
            text="Lihat Detail & Status",
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("#2563EB", "#1D4ED8"),
            command=lambda it=item: ItemDetailDialog(self.winfo_toplevel(), it, self.dm, on_update_callback=self._refresh_list_tab),
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
                on_action_callback=self._on_match_action_completed,
            )
        else:
            messagebox.showinfo("Auto-Matcher", f"Belum ditemukan kecocokan untuk {item.name} ({item.id}).")
