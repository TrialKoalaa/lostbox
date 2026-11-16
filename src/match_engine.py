"""
match_engine.py
Engine pencocokan otomatis (Auto Matcher) antara laporan barang hilang dan temuan.
Menerapkan konsep Python:
- Percabangan (Matching condition & scoring logic)
- Perulangan & Pemrosesan List / Dictionary
- String & Date Manipulation
- Exception Handling
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from src.models import Item, LostItem, FoundItem, Location


class MatchEngine:
    """
    Mesin pencocokan otomatis antara LostItem dan FoundItem.
    """

    STOPWORDS = {
        "di", "dan", "yang", "ini", "itu", "ada", "dengan", "ke", "dari", 
        "untuk", "pada", "adalah", "saat", "warna", "sebuah", "milik"
    }

    def __init__(self, lost_items: Optional[List[LostItem]] = None, found_items: Optional[List[FoundItem]] = None):
        self.lost_items: List[LostItem] = lost_items or []
        self.found_items: List[FoundItem] = found_items or []

    def set_items(self, lost_items: List[LostItem], found_items: List[FoundItem]):
        self.lost_items = lost_items
        self.found_items = found_items

    @classmethod
    def _extract_keywords(cls, text: str) -> set:
        """Ekstraksi kata kunci unik (lowercase, alphanumeric, tanpa stopword)."""
        import re
        words = re.findall(r"\w+", text.lower())
        return {w for w in words if len(w) >= 3 and w not in cls.STOPWORDS}

    @classmethod
    def calculate_score(cls, item_a: Item, item_b: Item) -> Tuple[float, Dict[str, Any], List[str]]:
        """
        Menghitung persentase kecocokan (0 - 100%) antara dua barang.
        Komponen:
        - Kategori (Exact match): 30%
        - Warna (Exact match): 20%
        - Lokasi: Same room (25%), Same floor (15%)
        - Waktu: Rentang +-3 hari (maks 15%)
        - Keyword nama & deskripsi (Substring / Jaccard token match): maks 10%
        """
        score = 0.0
        reasons = []
        breakdown = {
            "category": 0.0,
            "color": 0.0,
            "location": 0.0,
            "time": 0.0,
            "keyword": 0.0,
        }

        # 1. Kategori (30%)
        if item_a.category.strip().lower() == item_b.category.strip().lower():
            score += 30.0
            breakdown["category"] = 30.0
            reasons.append(f"Kategori sama ({item_a.category})")

        # 2. Warna (20%)
        if item_a.color.strip().lower() == item_b.color.strip().lower():
            score += 20.0
            breakdown["color"] = 20.0
            reasons.append(f"Warna sama ({item_a.color})")

        # 3. Lokasi (25% jika ruangan sama, 15% jika lantai sama)
        loc_a: Location = item_a.location
        loc_b: Location = item_b.location
        if loc_a.room_code.strip().lower() == loc_b.room_code.strip().lower():
            score += 25.0
            breakdown["location"] = 25.0
            reasons.append(f"Ruangan sama ({loc_a.room_name})")
        elif loc_a.floor == loc_b.floor:
            score += 15.0
            breakdown["location"] = 15.0
            reasons.append(f"Lantai sama (Lantai {loc_a.floor})")

        # 4. Waktu / Tanggal (+-3 hari rentang, maks 15%)
        try:
            d_a = datetime.strptime(item_a.date.strip(), "%Y-%m-%d").date()
            d_b = datetime.strptime(item_b.date.strip(), "%Y-%m-%d").date()
            day_diff = abs((d_a - d_b).days)
            if day_diff == 0:
                score += 15.0
                breakdown["time"] = 15.0
                reasons.append("Tanggal laporan sama persis")
            elif day_diff == 1:
                score += 12.0
                breakdown["time"] = 12.0
                reasons.append("Waktu sangat dekat (selisih 1 hari)")
            elif day_diff == 2:
                score += 8.0
                breakdown["time"] = 8.0
                reasons.append("Waktu berdekatan (selisih 2 hari)")
            elif day_diff <= 3:
                score += 5.0
                breakdown["time"] = 5.0
                reasons.append("Waktu dalam rentang 3 hari")
        except Exception:
            # Format tanggal tidak valid atau kosong
            pass

        # 5. Keyword Matching (nama & deskripsi, maks 10%)
        tokens_a = cls._extract_keywords(f"{item_a.name} {item_a.description}")
        tokens_b = cls._extract_keywords(f"{item_b.name} {item_b.description}")

        common_tokens = tokens_a.intersection(tokens_b)
        if common_tokens:
            # Hitung proporsi kesamaan kata
            overlap_ratio = len(common_tokens) / max(1, min(len(tokens_a), len(tokens_b)))
            kw_score = min(10.0, round(overlap_ratio * 10.0, 1))
            score += kw_score
            breakdown["keyword"] = kw_score
            matched_words = ", ".join(list(common_tokens)[:3])
            reasons.append(f"Kata kunci cocok: '{matched_words}'")
        else:
            # Substring match langsung nama barang
            name_a = item_a.name.strip().lower()
            name_b = item_b.name.strip().lower()
            if name_a in name_b or name_b in name_a:
                score += 8.0
                breakdown["keyword"] = 8.0
                reasons.append("Substring nama barang cocok")

        final_score = round(min(100.0, score), 1)
        return final_score, breakdown, reasons

    def find_matches(
        self,
        target_item: Item,
        candidate_items: Optional[List[Item]] = None,
        min_score: float = 40.0,
    ) -> List[Dict[str, Any]]:
        """
        Mencari kandidat kecocokan untuk target_item.
        Jika target_item adalah LostItem, kandidat dicari dari found_items.
        Jika target_item adalah FoundItem, kandidat dicari dari lost_items.
        Hanya mencocokkan laporan yang statusnya aktif ('Dilaporkan' atau 'Dicocokkan').
        """
        if candidate_items is None:
            if isinstance(target_item, LostItem):
                candidate_items = [
                    item for item in self.found_items if item.status in ("Dilaporkan", "Dicocokkan")
                ]
            else:
                candidate_items = [
                    item for item in self.lost_items if item.status in ("Dilaporkan", "Dicocokkan")
                ]

        results = []
        for candidate in candidate_items:
            # Jangan bandingkan barang dengan ID yang sama
            if candidate.id == target_item.id:
                continue

            score, breakdown, reasons = self.calculate_score(target_item, candidate)
            if score >= min_score:
                results.append({
                    "target_id": target_item.id,
                    "target_item": target_item,
                    "candidate_id": candidate.id,
                    "candidate_item": candidate,
                    "score": score,
                    "breakdown": breakdown,
                    "reasons": reasons,
                })

        return self.rank_results(results)

    @staticmethod
    def rank_results(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mengurutkan hasil pencocokan dari persentase skor tertinggi ke terendah."""
        return sorted(matches, key=lambda m: m["score"], reverse=True)
