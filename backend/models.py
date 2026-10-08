from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict


@dataclass
class Incident:
    incident_id: str
    latitude: float
    longitude: float
    date: str
    waste_type: str
    quantity_tonnes: float
    is_synthetic: bool
    ground_truth_company: Optional[str]
    description: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Facility:
    company_id: str
    company_name: str
    latitude: float
    longitude: float
    coord_type: str
    industry: str
    products: str
    waste_types: str
    production_capacity_tpa: Optional[float]
    regulatory_status: str
    address: str
    source_url: str
    source_note: str

    def to_dict(self):
        return asdict(self)


@dataclass
class WasteProfile:
    company_id: str
    waste_type: str
    waste_description: str
    authorized_quantity: Optional[float]
    source_document: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Evidence:
    company_id: str
    evidence_type: str
    description: str
    source_url: str
    document_name: str

    def to_dict(self):
        return asdict(self)


@dataclass
class HistoricalCase:
    case_id: str
    case_name: str
    date: str
    known_source: str
    location_context: str
    incident_type: str
    source_url: str
    notes: str

    def to_dict(self):
        return asdict(self)
