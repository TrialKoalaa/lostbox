"""
test_backend.py
Unit tests untuk memverifikasi logika backend:
- Class Location, Item, LostItem, FoundItem
- MatchEngine & Scoring Algorithm
- DataManager (CRUD, Filter, Statistics, ID Generator)
- Exception & Validation Handling
"""

import os
import shutil
import unittest
from datetime import datetime

from src.models import Location, Item, LostItem, FoundItem
from src.match_engine import MatchEngine
from src.data_manager import DataManager, ValidationError
from src.sample_data import get_initial_lost_items, get_initial_found_items


class TestLostBoxBackend(unittest.TestCase):

    def setUp(self):
        self.test_dir = "tests/test_data"
        os.makedirs(self.test_dir, exist_ok=True)
        self.dm = DataManager(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_location_model(self):
        loc1 = Location(2, "Lab Komputer 201", "LAB201")
        loc2 = Location(2, "Lab Komputer 201", "LAB201")
        loc3 = Location(1, "Ruang Kuliah 101", "R101")

        self.assertEqual(loc1, loc2)
        self.assertNotEqual(loc1, loc3)
        self.assertEqual(loc1.to_tuple(), (2, "LAB201", "Lab Komputer 201"))
        self.assertIn("Lt. 2", str(loc1))

    def test_item_hierarchy_and_status(self):
        loc = Location(1, "Lobby / Hall", "LOBBY")
        lost = LostItem("LOST-2026-999", "Botol Tupperware", "Botol / Tumbler", "Biru", "Hilang tadi pagi", loc, "2026-11-16", "08:30", "Dilaporkan", "Rizky")
        found = FoundItem("FOUND-2026-999", "Botol Tupperware", "Botol / Tumbler", "Biru", "Ditemukan di bangku", loc, "2026-11-16", "09:00", "Dilaporkan", "Satpam", kept_at="Dititipkan ke TU")

        self.assertEqual(lost.item_type, "LOST")
        self.assertEqual(found.item_type, "FOUND")
        self.assertEqual(found.kept_at, "Dititipkan ke TU")

        # Test Status Transition
        self.assertTrue(lost.update_status("Dicocokkan"))
        self.assertEqual(lost.status, "Dicocokkan")

        with self.assertRaises(ValueError):
            lost.update_status("StatusTidakDikenal")

    def test_id_generator(self):
        id1 = self.dm.generate_id("LOST")
        year = datetime.now().year
        self.assertTrue(id1.startswith(f"LOST-{year}-"))

    def test_validation(self):
        loc = Location(1, "Lobby / Hall", "LOBBY")
        # Empty reporter
        with self.assertRaises(ValidationError):
            self.dm.validate_item_input({
                "reporter": "",
                "name": "Barang",
                "category": "Elektronik",
                "color": "Hitam",
                "date": "2026-11-16",
                "time": "10:00",
                "location": loc.to_dict()
            })

        # Invalid date format
        with self.assertRaises(ValidationError):
            self.dm.validate_item_input({
                "reporter": "Budi",
                "name": "Barang",
                "category": "Elektronik",
                "color": "Hitam",
                "date": "16/11/2026",
                "time": "10:00",
                "location": loc.to_dict()
            })

    def test_match_engine_scenario(self):
        """
        Skenario Demo Halaman 17:
        Ahmad kehilangan charger laptop Asus di Lab Komputer 201.
        Budi menemukan charger laptop Asus hitam di Lab Komputer 201.
        Kecocokan harus sangat tinggi (>90%).
        """
        loc_lab = Location(2, "Lab Komputer 201", "LAB201")
        lost_ahmad = LostItem(
            item_id="LOST-001",
            name="Charger Laptop Asus",
            category="Elektronik",
            color="Hitam",
            description="Charger laptop Asus 65W, ada stiker",
            location=loc_lab,
            date="2026-11-14",
            time="10:30",
            status="Dilaporkan",
            reporter="Ahmad Rizky"
        )

        found_budi = FoundItem(
            item_id="FOUND-001",
            name="Charger Laptop Hitam",
            category="Elektronik",
            color="Hitam",
            description="Adapter charger laptop Asus 65W tertinggal",
            location=loc_lab,
            date="2026-11-14",
            time="12:00",
            status="Dilaporkan",
            reporter="Budi Santoso",
            kept_at="Dititipkan ke TU"
        )

        engine = MatchEngine(lost_items=[lost_ahmad], found_items=[found_budi])
        score, breakdown, reasons = engine.calculate_score(lost_ahmad, found_budi)

        self.assertGreaterEqual(score, 90.0)
        self.assertEqual(breakdown["category"], 30.0)
        self.assertEqual(breakdown["color"], 20.0)
        self.assertEqual(breakdown["location"], 25.0)
        self.assertEqual(breakdown["time"], 15.0)

        # Test find_matches
        matches = engine.find_matches(lost_ahmad)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["candidate_id"], "FOUND-001")

    def test_statistics_calculation(self):
        # Insert sample data to test stats
        for item in get_initial_lost_items():
            self.dm.add_lost_item(item)
        for item in get_initial_found_items():
            self.dm.add_found_item(item)

        stats = self.dm.get_statistics()
        self.assertGreater(stats["total_reports"], 10)
        self.assertGreater(stats["return_rate"], 0.0)
        self.assertTrue(len(stats["hotspots"]) > 0)
        self.assertTrue("Elektronik" in stats["categories"])


if __name__ == "__main__":
    unittest.main()
