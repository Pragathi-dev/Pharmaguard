from enum import Enum


class SiteObservationStatus(str, Enum):
    """
    Standardized observation status for every catalogued pharmacogene site.
    Preserves missingness by distinguishing true homozygous reference from absent data.
    """
    HOM_REF = "HOM_REF"
    HET = "HET"
    HOM_ALT = "HOM_ALT"
    NO_CALL = "NO_CALL"
    NOT_IN_VCF = "NOT_IN_VCF"
    FILTERED = "FILTERED"
    MULTIALLELIC = "MULTIALLELIC"
    LOW_QUALITY = "LOW_QUALITY"


class ReferenceEvidence(str, Enum):
    """
    Supporting evidence category for a homozygous reference call.
    """
    EXPLICIT_GT = "explicit_gt"
    GVCF_BLOCK = "gvcf_block"
    CALLABLE_BED = "callable_bed"
    NONE = "none"
