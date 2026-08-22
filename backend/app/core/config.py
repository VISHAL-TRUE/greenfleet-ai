"""
GreenFlow AI - Core Configuration & Environmental Parameters
"""

from typing import Dict
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "GreenFlow AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Deterministic simulation seed
    RANDOM_SEED: int = 42
    
    # DEFRA / UK Gov GHG Standard Conversion Factors (kg CO2 per litre of fuel)
    EMISSION_FACTORS_KG_CO2_PER_LITRE: Dict[str, float] = {
        "Diesel": 2.68,
        "Petrol": 2.31,
        "Hybrid": 2.31,
        "CNG": 1.95,
        "Default": 2.65,
    }
    
    # Regional Fleet Fuel Pricing ($ per litre)
    FUEL_PRICES_PER_LITRE: Dict[str, float] = {
        "Diesel": 1.65,
        "Petrol": 1.55,
        "Hybrid": 1.55,
        "CNG": 1.10,
        "Default": 1.60,
    }
    
    # Baseline Operating Cost per KM ($/km by vehicle category)
    VEHICLE_TYPE_BASE_COST_PER_KM: Dict[str, float] = {
        "Van": 0.45,
        "Light Commercial": 0.75,
        "Truck": 1.25,
        "Semi-Trailer": 2.10,
        "Bus": 1.50,
        "Default": 0.95,
    }

    # Inefficiency threshold: If assigned vehicle fuel consumption exceeds 1.35x minimum possible for that route
    INEFFICIENCY_THRESHOLD_RATIO: float = 1.35


settings = Settings()
