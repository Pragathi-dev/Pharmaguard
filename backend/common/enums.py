from enum import Enum


class ProvenanceClass(str, Enum):
    """
    Standardized classification for dataset provenance tracking.
    Strictly enforced across training, validation, and inference pipelines.
    """
    REAL_PATIENT_GENOTYPE = "REAL_PATIENT_GENOTYPE"
    REAL_REFERENCE_LABEL = "REAL_REFERENCE_LABEL"
    DERIVED_SILVER_LABEL = "DERIVED_SILVER_LABEL"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    POPULATION_AGGREGATE = "POPULATION_AGGREGATE"
    PHARMACOVIGILANCE_CONTEXT = "PHARMACOVIGILANCE_CONTEXT"
    AUGMENTED_REAL = "AUGMENTED_REAL"
    SYNTHETIC_RECOMBINANT = "SYNTHETIC_RECOMBINANT"
