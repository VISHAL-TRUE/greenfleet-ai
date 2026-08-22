"""
GreenFlow AI - Route Data Model
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RouteModel(BaseModel):
    """
    Route representation adhering strictly to Person 3 & ML team contracts.
    """
    route_id: str = Field(..., description="Unique route identifier (e.g. R001)")
    origin: str = Field(..., description="Starting point / departure hub")
    destination: str = Field(..., description="Delivery destination")
    distance_km: float = Field(..., gt=0, description="Total route distance in kilometres")
    required_payload_kg: float = Field(..., ge=0, description="Cargo weight required for this route in kg")
    traffic_factor: float = Field(default=1.0, ge=0.5, le=3.0, description="Congestion multiplier (1.0 = normal, 1.5 = heavy)")
    priority: int = Field(default=1, ge=1, le=5, description="Delivery priority level (1 = normal, 5 = critical)")
    
    # Optional operational metadata
    time_window: Optional[str] = Field(default="08:00-12:00", description="Scheduled delivery window")
    departure_time: Optional[str] = Field(default="08:00", description="Expected departure time")
    road_grade: Optional[float] = Field(default=0.0, description="Average road incline percentage")
    weather_factor: Optional[float] = Field(default=1.0, description="Adverse weather impact multiplier")

    model_config = {
        "json_schema_extra": {
            "example": {
                "route_id": "R001",
                "origin": "Depot Central",
                "destination": "Industrial Zone East",
                "distance_km": 65.0,
                "required_payload_kg": 3200.0,
                "traffic_factor": 1.2,
                "priority": 2,
                "time_window": "09:00-13:00"
            }
        }
    }


class RouteListResponse(BaseModel):
    """API response for route listing."""
    total_routes: int
    total_distance_km: float
    total_payload_kg: float
    routes: List[RouteModel]
