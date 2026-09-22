"""
Database models backed by Supabase.

Supabase Python client (v2) types `response.data` as `list[Any] | None`.
Every helper that reads `response.data` therefore uses the private
`_rows()` utility so that:
  - the type-checker always sees a plain `list[dict]` (never `None`)
  - runtime is safe even when Supabase returns an empty / null payload
"""

import json
from typing import Any
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _rows(response: Any) -> list[dict]:
    """
    Safely coerce ``response.data`` (typed ``list[Any] | None`` in Supabase v2)
    into a plain ``list[dict]``.

    * If ``response.data`` is ``None`` or falsy returns ``[]``.
    * Non-dict elements are skipped (defensive; should not occur normally).
    """
    raw = getattr(response, "data", None)
    if not raw:
        return []
    result: list[dict] = []
    for item in raw:
        if isinstance(item, dict):
            result.append(item)
    return result


def _first_row(response: Any) -> dict | None:
    """Return the first row as a ``dict``, or ``None`` if the response is empty."""
    rows = _rows(response)
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# User
# Fields: id, username, email, password_hash, role, created_at
# ---------------------------------------------------------------------------

class User:
    def __init__(
        self,
        id: Any,
        username: Any,
        email: Any,
        password_hash: Any,
        role: Any = "user",
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def create(cls, username: str, email: str, password: str, role: str = "user") -> "User | None":
        supabase = get_db()
        hashed_password = cls.hash_password(password)
        data = {
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "role": role,
        }
        response = supabase.table("users").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_by_username(cls, username: str) -> "User | None":
        supabase = get_db()
        response = supabase.table("users").select("*").eq("username", username).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_by_email(cls, email: str) -> "User | None":
        supabase = get_db()
        response = supabase.table("users").select("*").eq("email", email).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_by_id(cls, user_id: Any) -> "User | None":
        supabase = get_db()
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_all(cls) -> "list[User]":
        supabase = get_db()
        response = supabase.table("users").select("*").order("id").execute()
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def delete(cls, user_id: Any) -> bool:
        supabase = get_db()
        supabase.table("users").delete().eq("id", user_id).execute()
        return True


# ---------------------------------------------------------------------------
# WasteCategory
# Fields: id, category_name, waste_type, recommended_bin_color,
#         disposal_suggestion, created_at
# ---------------------------------------------------------------------------

class WasteCategory:
    def __init__(
        self,
        id: Any,
        category_name: Any,
        waste_type: Any,
        recommended_bin_color: Any,
        disposal_suggestion: Any,
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.category_name = category_name
        self.waste_type = waste_type
        self.recommended_bin_color = recommended_bin_color
        self.disposal_suggestion = disposal_suggestion
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_name": self.category_name,
            "waste_type": self.waste_type,
            "recommended_bin_color": self.recommended_bin_color,
            "disposal_suggestion": self.disposal_suggestion,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def get_all(cls) -> "list[WasteCategory]":
        supabase = get_db()
        response = supabase.table("waste_categories").select("*").order("id").execute()
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def create(
        cls,
        category_name: str,
        waste_type: str,
        recommended_bin_color: str,
        disposal_suggestion: str,
    ) -> "WasteCategory | None":
        supabase = get_db()
        data = {
            "category_name": category_name,
            "waste_type": waste_type,
            "recommended_bin_color": recommended_bin_color,
            "disposal_suggestion": disposal_suggestion,
        }
        response = supabase.table("waste_categories").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def delete(cls, category_id: Any) -> bool:
        supabase = get_db()
        supabase.table("waste_categories").delete().eq("id", category_id).execute()
        return True


# ---------------------------------------------------------------------------
# Dumpyard
# Fields: id, name, address, latitude, longitude, contact,
#         admin_id, status, created_at
# ---------------------------------------------------------------------------

class Dumpyard:
    def __init__(
        self,
        id: Any,
        name: Any,
        address: Any,
        latitude: Any,
        longitude: Any,
        contact: Any,
        admin_id: Any,
        status: Any = "ACTIVE",
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.name = name
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.contact = contact
        self.admin_id = admin_id
        self.status = status
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "contact": self.contact,
            "admin_id": self.admin_id,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def get_all(cls) -> "list[Dumpyard]":
        supabase = get_db()
        response = supabase.table("dumpyards").select("*").order("id").execute()
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def get_by_id(cls, id: Any) -> "Dumpyard | None":
        supabase = get_db()
        response = supabase.table("dumpyards").select("*").eq("id", id).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None


# ---------------------------------------------------------------------------
# Vehicle
# Fields: id, registration_number, vehicle_type, capacity_kg, dumpyard_id,
#         status, current_latitude, current_longitude, last_updated
# ---------------------------------------------------------------------------

class Vehicle:
    def __init__(
        self,
        id: Any,
        registration_number: Any,
        vehicle_type: Any,
        capacity_kg: Any,
        dumpyard_id: Any,
        status: Any = "AVAILABLE",
        current_latitude: Any = None,
        current_longitude: Any = None,
        last_updated: Any = None,
    ) -> None:
        self.id = id
        self.registration_number = registration_number
        self.vehicle_type = vehicle_type
        self.capacity_kg = capacity_kg
        self.dumpyard_id = dumpyard_id
        self.status = status
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.last_updated = last_updated

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "registration_number": self.registration_number,
            "vehicle_type": self.vehicle_type,
            "capacity_kg": self.capacity_kg,
            "dumpyard_id": self.dumpyard_id,
            "status": self.status,
            "current_latitude": self.current_latitude,
            "current_longitude": self.current_longitude,
            "last_updated": str(self.last_updated) if self.last_updated else None,
        }

    @classmethod
    def get_all(cls) -> "list[Vehicle]":
        supabase = get_db()
        response = supabase.table("vehicles").select("*").order("id").execute()
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def get_by_dumpyard(cls, dumpyard_id: Any) -> "list[Vehicle]":
        supabase = get_db()
        response = (
            supabase.table("vehicles")
            .select("*")
            .eq("dumpyard_id", dumpyard_id)
            .execute()
        )
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def update_status(cls, vehicle_id: Any, status: str) -> "Vehicle | None":
        supabase = get_db()
        response = (
            supabase.table("vehicles")
            .update({"status": status})
            .eq("id", vehicle_id)
            .execute()
        )
        row = _first_row(response)
        return cls(**row) if row is not None else None


# ---------------------------------------------------------------------------
# Driver
# Fields: id, user_id, name, phone, email, license_number,
#         dumpyard_id, status, created_at
# ---------------------------------------------------------------------------

class Driver:
    def __init__(
        self,
        id: Any,
        user_id: Any,
        name: Any,
        phone: Any,
        email: Any,
        license_number: Any,
        dumpyard_id: Any,
        status: Any = "AVAILABLE",
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.license_number = license_number
        self.dumpyard_id = dumpyard_id
        self.status = status
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "license_number": self.license_number,
            "dumpyard_id": self.dumpyard_id,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def get_by_user_id(cls, user_id: Any) -> "Driver | None":
        supabase = get_db()
        response = (
            supabase.table("drivers").select("*").eq("user_id", user_id).execute()
        )
        row = _first_row(response)
        return cls(**row) if row is not None else None


# ---------------------------------------------------------------------------
# WasteReport
# Fields: id, citizen_id, image_url, description, waste_type, latitude,
#         longitude, address, priority, status, assigned_dumpyard_id,
#         assigned_vehicle_id, assigned_driver_id, completion_proof_url,
#         ai_verification_status, confidence_score, created_at
# ---------------------------------------------------------------------------

class WasteReport:
    def __init__(
        self,
        id: Any,
        citizen_id: Any,
        image_url: Any,
        description: Any,
        waste_type: Any,
        latitude: Any,
        longitude: Any,
        address: Any,
        priority: Any = 1,
        status: Any = "SUBMITTED",
        assigned_dumpyard_id: Any = None,
        assigned_vehicle_id: Any = None,
        assigned_driver_id: Any = None,
        completion_proof_url: Any = None,
        ai_verification_status: Any = None,
        confidence_score: Any = None,
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.citizen_id = citizen_id
        self.image_url = image_url
        self.description = description
        self.waste_type = waste_type
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.priority = priority
        self.status = status
        self.assigned_dumpyard_id = assigned_dumpyard_id
        self.assigned_vehicle_id = assigned_vehicle_id
        self.assigned_driver_id = assigned_driver_id
        self.completion_proof_url = completion_proof_url
        self.ai_verification_status = ai_verification_status
        self.confidence_score = confidence_score
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "citizen_id": self.citizen_id,
            "image_url": self.image_url,
            "description": self.description,
            "waste_type": self.waste_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "priority": self.priority,
            "status": self.status,
            "assigned_dumpyard_id": self.assigned_dumpyard_id,
            "assigned_vehicle_id": self.assigned_vehicle_id,
            "assigned_driver_id": self.assigned_driver_id,
            "completion_proof_url": self.completion_proof_url,
            "ai_verification_status": self.ai_verification_status,
            "confidence_score": self.confidence_score,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        citizen_id: Any,
        image_url: str,
        description: str,
        waste_type: str,
        latitude: float,
        longitude: float,
        address: str,
        assigned_dumpyard_id: Any = None,
    ) -> "WasteReport | None":
        supabase = get_db()
        data = {
            "citizen_id": citizen_id,
            "image_url": image_url,
            "description": description,
            "waste_type": waste_type,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
        }
        if assigned_dumpyard_id is not None:
            data["assigned_dumpyard_id"] = assigned_dumpyard_id
        response = supabase.table("waste_reports").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_all(cls) -> "list[WasteReport]":
        supabase = get_db()
        response = (
            supabase.table("waste_reports").select("*").order("id", desc=True).execute()
        )
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def get_by_id(cls, report_id: Any) -> "WasteReport | None":
        supabase = get_db()
        response = supabase.table("waste_reports").select("*").eq("id", report_id).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def update_status(
        cls,
        report_id: Any,
        status: str,
        dumpyard_id: Any = None,
        vehicle_id: Any = None,
        driver_id: Any = None,
        completion_proof_url: Any = None,
        ai_verification_status: Any = None,
    ) -> "WasteReport | None":
        supabase = get_db()
        data: dict = {"status": status}
        if dumpyard_id is not None:
            data["assigned_dumpyard_id"] = dumpyard_id
        if vehicle_id is not None:
            data["assigned_vehicle_id"] = vehicle_id
        if driver_id is not None:
            data["assigned_driver_id"] = driver_id
        if completion_proof_url is not None:
            data["completion_proof_url"] = completion_proof_url
        if ai_verification_status is not None:
            data["ai_verification_status"] = ai_verification_status
        response = (
            supabase.table("waste_reports").update(data).eq("id", report_id).execute()
        )
        row = _first_row(response)
        return cls(**row) if row is not None else None


# ---------------------------------------------------------------------------
# CollectionTask
# Fields: id, dumpyard_id, vehicle_id, driver_id, report_id, status, created_at
# ---------------------------------------------------------------------------

class CollectionTask:
    def __init__(
        self,
        id: Any,
        dumpyard_id: Any,
        vehicle_id: Any,
        driver_id: Any,
        report_id: Any,
        status: Any = "PENDING",
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.dumpyard_id = dumpyard_id
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.report_id = report_id
        self.status = status
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "dumpyard_id": self.dumpyard_id,
            "vehicle_id": self.vehicle_id,
            "driver_id": self.driver_id,
            "report_id": self.report_id,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        dumpyard_id: Any,
        vehicle_id: Any,
        driver_id: Any,
        report_id: Any,
    ) -> "CollectionTask | None":
        supabase = get_db()
        data = {
            "dumpyard_id": dumpyard_id,
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "report_id": report_id,
        }
        response = supabase.table("collection_tasks").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None


# ---------------------------------------------------------------------------
# StatusHistory
# Fields: id, report_id, status, remarks, changed_by, created_at
# ---------------------------------------------------------------------------

class StatusHistory:
    def __init__(
        self,
        id: Any,
        report_id: Any,
        status: Any,
        remarks: Any,
        changed_by: Any,
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.report_id = report_id
        self.status = status
        self.remarks = remarks
        self.changed_by = changed_by
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "report_id": self.report_id,
            "status": self.status,
            "remarks": self.remarks,
            "changed_by": self.changed_by,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        report_id: Any,
        status: str,
        remarks: Any = None,
        changed_by: Any = None,
    ) -> "StatusHistory | None":
        supabase = get_db()
        data = {
            "report_id": report_id,
            "status": status,
            "remarks": remarks,
            "changed_by": changed_by,
        }
        response = supabase.table("status_history").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None


# ---------------------------------------------------------------------------
# Route
# Fields: id, route_name, depot_lat, depot_lng, total_distance_km,
#         estimated_time_mins, fuel_used_liters, visited_bins_count,
#         stops_json, created_at
# ---------------------------------------------------------------------------

class Route:
    def __init__(
        self,
        id: Any,
        route_name: Any,
        depot_lat: Any,
        depot_lng: Any,
        total_distance_km: Any,
        estimated_time_mins: Any,
        fuel_used_liters: Any,
        visited_bins_count: Any,
        stops_json: Any,
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.route_name = route_name
        self.depot_lat = depot_lat
        self.depot_lng = depot_lng
        self.total_distance_km = total_distance_km
        self.estimated_time_mins = estimated_time_mins
        self.fuel_used_liters = fuel_used_liters
        self.visited_bins_count = visited_bins_count
        # Normalise: always store as a JSON string internally so that
        # to_dict() can parse it safely regardless of what Supabase returns
        # (some drivers may return already-decoded list/dict).
        if isinstance(stops_json, (list, dict)):
            self.stops_json: str = json.dumps(stops_json)
        elif isinstance(stops_json, str):
            self.stops_json = stops_json
        else:
            self.stops_json = "[]"
        self.created_at = created_at

    def to_dict(self) -> dict:
        try:
            stops = json.loads(self.stops_json)
        except (json.JSONDecodeError, TypeError):
            stops = []
        return {
            "id": self.id,
            "route_name": self.route_name,
            "depot_lat": self.depot_lat,
            "depot_lng": self.depot_lng,
            "total_distance_km": self.total_distance_km,
            "estimated_time_mins": self.estimated_time_mins,
            "fuel_used_liters": self.fuel_used_liters,
            "visited_bins_count": self.visited_bins_count,
            "stops": stops,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        route_name: str,
        depot_lat: float,
        depot_lng: float,
        total_distance_km: float,
        estimated_time_mins: float,
        fuel_used_liters: float,
        visited_bins_count: int,
        stops_list: list,
    ) -> "Route | None":
        supabase = get_db()
        stops_str = json.dumps(stops_list)
        data = {
            "route_name": route_name,
            "depot_lat": depot_lat,
            "depot_lng": depot_lng,
            "total_distance_km": total_distance_km,
            "estimated_time_mins": estimated_time_mins,
            "fuel_used_liters": fuel_used_liters,
            "visited_bins_count": visited_bins_count,
            "stops_json": stops_str,
        }
        response = supabase.table("routes").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_recent(cls, limit: int = 5) -> "list[Route]":
        supabase = get_db()
        response = (
            supabase.table("routes")
            .select("*")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def get_all(cls) -> "list[Route]":
        supabase = get_db()
        response = (
            supabase.table("routes").select("*").order("id", desc=True).execute()
        )
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def delete(cls, route_id: Any) -> bool:
        supabase = get_db()
        supabase.table("routes").delete().eq("id", route_id).execute()
        return True


# ---------------------------------------------------------------------------
# WasteDetection
# Fields: id, category_name, waste_type, bin_color, confidence_score,
#         image_path, disposal_suggestion, user_id, detected_at
# ---------------------------------------------------------------------------

class WasteDetection:
    def __init__(
        self,
        id: Any,
        category_name: Any,
        waste_type: Any,
        bin_color: Any,
        confidence_score: Any,
        image_path: Any,
        disposal_suggestion: Any,
        user_id: Any = None,
        detected_at: Any = None,
    ) -> None:
        self.id = id
        self.category_name = category_name
        self.waste_type = waste_type
        self.bin_color = bin_color
        self.confidence_score = confidence_score
        self.image_path = image_path
        self.disposal_suggestion = disposal_suggestion
        self.user_id = user_id
        self.detected_at = detected_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_name": self.category_name,
            "waste_type": self.waste_type,
            "bin_color": self.bin_color,
            "confidence_score": self.confidence_score,
            "image_path": self.image_path,
            "disposal_suggestion": self.disposal_suggestion,
            "user_id": self.user_id,
            "detected_at": str(self.detected_at) if self.detected_at else None,
        }

    @classmethod
    def create(
        cls,
        category_name: str,
        waste_type: str,
        bin_color: str,
        confidence_score: float,
        image_path: str,
        disposal_suggestion: str,
        user_id: Any = None,
    ) -> "WasteDetection | None":
        supabase = get_db()
        data = {
            "category_name": category_name,
            "waste_type": waste_type,
            "bin_color": bin_color,
            "confidence_score": confidence_score,
            "image_path": image_path,
            "disposal_suggestion": disposal_suggestion,
            "user_id": user_id,
        }
        response = supabase.table("waste_detections").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_recent(cls, limit: int = 15) -> "list[WasteDetection]":
        supabase = get_db()
        response = (
            supabase.table("waste_detections")
            .select("*")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def get_all(cls) -> "list[WasteDetection]":
        supabase = get_db()
        response = (
            supabase.table("waste_detections")
            .select("*")
            .order("id", desc=True)
            .execute()
        )
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def delete(cls, detection_id: Any) -> bool:
        supabase = get_db()
        supabase.table("waste_detections").delete().eq("id", detection_id).execute()
        return True


# ---------------------------------------------------------------------------
# Location
# Fields: id, location_name, latitude, longitude, capacity_kg,
#         current_fill_level, current_weight_kg, priority, status, created_at
# Status rules: >= 90 -> Overflown  |  >= 60 -> Needs Collection  |  < 60 -> Normal
# ---------------------------------------------------------------------------

class Location:
    @staticmethod
    def calculate_status(fill_level: float) -> str:
        if fill_level >= 90.0:
            return "Overflown"
        if fill_level >= 60.0:
            return "Needs Collection"
        return "Normal"

    def __init__(
        self,
        id: Any,
        location_name: Any,
        latitude: Any,
        longitude: Any,
        capacity_kg: Any = 100.0,
        current_fill_level: Any = 0.0,
        current_weight_kg: Any = 0.0,
        priority: Any = 1,
        status: Any = None,
        created_at: Any = None,
    ) -> None:
        self.id = id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.capacity_kg = capacity_kg
        self.current_fill_level = current_fill_level
        self.current_weight_kg = current_weight_kg
        self.priority = priority
        # Use the stored status from Supabase when available; derive otherwise.
        self.status = status if status else self.calculate_status(
            float(current_fill_level) if current_fill_level is not None else 0.0
        )
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacity_kg": self.capacity_kg,
            "current_fill_level": self.current_fill_level,
            "current_weight_kg": self.current_weight_kg,
            "priority": self.priority,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        location_name: str,
        latitude: float,
        longitude: float,
        capacity_kg: float = 100.0,
        current_fill_level: float = 0.0,
        current_weight_kg: float = 0.0,
        priority: int = 1,
        status: Any = None,
    ) -> "Location | None":
        supabase = get_db()
        calculated_status = status if status else cls.calculate_status(current_fill_level)
        data = {
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "capacity_kg": capacity_kg,
            "current_fill_level": current_fill_level,
            "current_weight_kg": current_weight_kg,
            "priority": priority,
            "status": calculated_status,
        }
        response = supabase.table("locations").insert(data).execute()
        row = _first_row(response)
        return cls(**row) if row is not None else None

    @classmethod
    def get_all(cls) -> "list[Location]":
        supabase = get_db()
        response = supabase.table("locations").select("*").order("id").execute()
        return [cls(**row) for row in _rows(response)]

    @classmethod
    def delete(cls, location_id: Any) -> bool:
        supabase = get_db()
        supabase.table("locations").delete().eq("id", location_id).execute()
        return True