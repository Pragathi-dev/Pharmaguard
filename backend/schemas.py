from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, List

# Request schema for the clinical endpoint
class ClinicalRequest(BaseModel):
    drug: str
    gene: str
    status: str  # Matches parser output: "Normal", "Intermediate", "Poor"

# Response schema for the clinical endpoint
class ClinicalRecommendation(BaseModel):
    drug: str
    gene: str
    status: str
    clinical_context: Optional[str] = None
    recommendation: str
    evidence_source: str = "CPIC"
    guideline_version: str
    evidence_level: str

# Doctor Registration Schema
class DoctorRegisterRequest(BaseModel):
    name: str
    doctor_id: str
    hospital: str
    email: str
    password: str

# Doctor Login Schema
class DoctorLoginRequest(BaseModel):
    email: str
    password: str

# Doctor Info Response Schema
class DoctorResponse(BaseModel):
    name: str
    doctor_id: str
    hospital: str
    email: str

# Token Response Schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    doctor: DoctorResponse