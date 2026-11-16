"""
models.py
Modul representasi objek (OOP) untuk LostBox:
- Location: representasi data lokasi (lantai, kode, nama ruangan)
- Item: kelas induk abstrak untuk barang
- LostItem: kelas turunan untuk barang hilang
- FoundItem: kelas turunan untuk barang temuan
"""

from typing import Dict, Any, Optional, Tuple


class Location:
    """
    Representasi lokasi di dalam Gedung Prodi.
    Menerapkan konsep OOP dan penggunaan Tuple/Dict.
    """
    def __init__(self, floor: int, room_name: str, room_code: str):
        self.floor: int = int(floor)
        self.room_name: str = room_name.strip()
        self.room_code: str = room_code.strip()

    def __str__(self) -> str:
        return f"Lt. {self.floor} - {self.room_name} ({self.room_code})"

    def __repr__(self) -> str:
        return f"Location(floor={self.floor}, room_name='{self.room_name}', room_code='{self.room_code}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return (
            self.floor == other.floor
            and self.room_code.upper() == other.room_code.upper()
        )

    def to_tuple(self) -> Tuple[int, str, str]:
        """Contoh penerapan tipe data Tuple untuk koordinat lokasi."""
        return (self.floor, self.room_code, self.room_name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "floor": self.floor,
            "room_code": self.room_code,
            "room_name": self.room_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        return cls(
            floor=data.get("floor", 1),
            room_name=data.get("room_name", "Unknown Room"),
            room_code=data.get("room_code", "UNKNOWN"),
        )


class Item:
    """
    Kelas induk (Base Class) untuk representasi laporan barang.
    Menerapkan konsep OOP (Inheritance, Encapsulation, Polymorphism).
    """

    VALID_STATUSES = {
        "Dilaporkan",
        "Dicocokkan",
        "Diklaim",
        "Selesai",
        "Kedaluwarsa",
    }

    def __init__(
        self,
        item_id: str,
        name: str,
        category: str,
        color: str,
        description: str,
        location: Location,
        date: str,
        time: str,
        status: str = "Dilaporkan",
        reporter: str = "",
    ):
        self._id: str = item_id
        self._name: str = name
        self._category: str = category
        self._color: str = color
        self._description: str = description
        self._location: Location = location
        self._date: str = date
        self._time: str = time
        self._status: str = status if status in self.VALID_STATUSES else "Dilaporkan"
        self._reporter: str = reporter

    # Property Getters
    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value.strip()

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str):
        self._category = value.strip()

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value.strip()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value.strip()

    @property
    def location(self) -> Location:
        return self._location

    @location.setter
    def location(self, value: Location):
        if not isinstance(value, Location):
            raise TypeError("Lokasi harus berupa objek Location")
        self._location = value

    @property
    def date(self) -> str:
        return self._date

    @property
    def time(self) -> str:
        return self._time

    @property
    def status(self) -> str:
        return self._status

    @property
    def reporter(self) -> str:
        return self._reporter

    @property
    def item_type(self) -> str:
        """Ditentukan oleh subclass."""
        return "ITEM"

    def update_status(self, new_status: str) -> bool:
        """
        Validasi dan update lifecycle status.
        Status flow: Dilaporkan -> Dicocokkan -> Diklaim -> Selesai
        Bisa juga kembali ke Dilaporkan jika match dibatalkan.
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Status '{new_status}' tidak valid. Pilihan: {self.VALID_STATUSES}")
        self._status = new_status
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialisasi objek ke bentuk dictionary untuk JSON."""
        return {
            "id": self._id,
            "name": self._name,
            "category": self._category,
            "color": self._color,
            "description": self._description,
            "location": self._location.to_dict(),
            "date": self._date,
            "time": self._time,
            "status": self._status,
            "reporter": self._reporter,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        loc_data = data.get("location", {})
        location_obj = (
            Location.from_dict(loc_data)
            if isinstance(loc_data, dict)
            else Location(1, "Unknown", "UNKNOWN")
        )
        return cls(
            item_id=data.get("id", ""),
            name=data.get("name", ""),
            category=data.get("category", "Lainnya"),
            color=data.get("color", "Lainnya"),
            description=data.get("description", ""),
            location=location_obj,
            date=data.get("date", ""),
            time=data.get("time", ""),
            status=data.get("status", "Dilaporkan"),
            reporter=data.get("reporter", ""),
        )

    def __str__(self) -> str:
        return f"[{self.item_type}] {self.id}: {self.name} ({self.category}, {self.color}) - Status: {self.status}"


class LostItem(Item):
    """
    Subclass untuk barang hilang (Inheritance dari Item).
    """

    @property
    def item_type(self) -> str:
        return "LOST"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LostItem":
        loc_data = data.get("location", {})
        location_obj = (
            Location.from_dict(loc_data)
            if isinstance(loc_data, dict)
            else Location(1, "Unknown", "UNKNOWN")
        )
        return cls(
            item_id=data.get("id", ""),
            name=data.get("name", ""),
            category=data.get("category", "Lainnya"),
            color=data.get("color", "Lainnya"),
            description=data.get("description", ""),
            location=location_obj,
            date=data.get("date", ""),
            time=data.get("time", ""),
            status=data.get("status", "Dilaporkan"),
            reporter=data.get("reporter", ""),
        )


class FoundItem(Item):
    """
    Subclass untuk barang temuan (Inheritance dari Item).
    Menambahkan atribut khusus 'kept_at' (status penyimpanan).
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        category: str,
        color: str,
        description: str,
        location: Location,
        date: str,
        time: str,
        status: str = "Dilaporkan",
        reporter: str = "",
        kept_at: str = "Dititipkan ke TU",
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            category=category,
            color=color,
            description=description,
            location=location,
            date=date,
            time=time,
            status=status,
            reporter=reporter,
        )
        self._kept_at: str = kept_at

    @property
    def kept_at(self) -> str:
        return self._kept_at

    @kept_at.setter
    def kept_at(self, value: str):
        self._kept_at = value.strip()

    @property
    def item_type(self) -> str:
        return "FOUND"

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["kept_at"] = self._kept_at
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FoundItem":
        loc_data = data.get("location", {})
        location_obj = (
            Location.from_dict(loc_data)
            if isinstance(loc_data, dict)
            else Location(1, "Unknown", "UNKNOWN")
        )
        return cls(
            item_id=data.get("id", ""),
            name=data.get("name", ""),
            category=data.get("category", "Lainnya"),
            color=data.get("color", "Lainnya"),
            description=data.get("description", ""),
            location=location_obj,
            date=data.get("date", ""),
            time=data.get("time", ""),
            status=data.get("status", "Dilaporkan"),
            reporter=data.get("reporter", ""),
            kept_at=data.get("kept_at", "Dititipkan ke TU"),
        )
