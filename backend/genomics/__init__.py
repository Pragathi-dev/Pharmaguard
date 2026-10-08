"""
PharmaGuard Genomics Subsystem
Package for site extraction, VCF parsing, variant normalization, and QC tracking.
"""
from backend.genomics.enums import SiteObservationStatus, ReferenceEvidence
from backend.genomics.catalogue import load_catalogue, CatalogueSite, Catalogue
from backend.genomics.normalize import normalize_variant, harmonize_contig
from backend.genomics.vcf_reader import read_vcf_records
from backend.genomics.callable import evaluate_callable_evidence
from backend.genomics.qc import apply_genotype_qc, compute_sample_qc
from backend.genomics.site_extractor import extract_site_calls

__all__ = [
    "SiteObservationStatus",
    "ReferenceEvidence",
    "load_catalogue",
    "CatalogueSite",
    "Catalogue",
    "normalize_variant",
    "harmonize_contig",
    "read_vcf_records",
    "evaluate_callable_evidence",
    "apply_genotype_qc",
    "compute_sample_qc",
    "extract_site_calls"
]
