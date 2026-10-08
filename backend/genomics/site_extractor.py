from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

from backend.common.enums import ProvenanceClass
from backend.common.hashing import sha256_file
from backend.common.logging_config import get_logger
from backend.genomics.catalogue import Catalogue, CatalogueSite
from backend.genomics.callable import parse_bed_file, evaluate_callable_evidence
from backend.genomics.enums import SiteObservationStatus, ReferenceEvidence
from backend.genomics.normalize import harmonize_contig, normalize_variant
from backend.genomics.qc import QcConfig, apply_genotype_qc
from backend.genomics.vcf_reader import read_vcf_records

logger = get_logger("pharmaguard.genomics.extractor")


def extract_site_calls(
    vcf_path: Union[str, Path],
    catalogue: Catalogue,
    qc_config: Optional[QcConfig] = None,
    target_samples: Optional[List[str]] = None,
    callable_bed_path: Optional[Union[str, Path]] = None,
    provenance_class: Optional[str] = None,
    source_sha256: Optional[str] = None,
    schema_version: str = "1.0"
) -> pd.DataFrame:
    """
    Extracts explicit site observations for all catalogued pharmacogene sites.
    Preserves missingness: absent sites become NOT_IN_VCF, never silently HOM_REF.

    Returns:
        pd.DataFrame: Long-format site_calls DataFrame.
    """
    if qc_config is None:
        qc_config = QcConfig()

    vcf_file = Path(vcf_path)
    if not vcf_file.is_file():
        raise FileNotFoundError(f"VCF file not found: {vcf_file}")

    if source_sha256 is None:
        source_sha256 = sha256_file(vcf_file)

    if provenance_class is None:
        provenance_class = ProvenanceClass.REAL_PATIENT_GENOTYPE.value

    # Parse callable BED if provided
    bed_intervals = parse_bed_file(callable_bed_path) if callable_bed_path else None

    # Read VCF records for all catalogued gene regions
    all_rows = []
    
    for gene_name, sites in catalogue.sites_by_gene.items():
        if not sites:
            continue

        # Determine region bounding box for vcf fetch
        chrom = sites[0].chrom
        min_pos = min(s.pos for s in sites)
        max_pos = max(s.pos for s in sites)

        vcf_records, vcf_samples, malformed_count = read_vcf_records(
            vcf_file, region_chrom=chrom, region_start=min_pos - 100, region_end=max_pos + 100
        )

        samples_to_process = target_samples if target_samples else vcf_samples
        if not samples_to_process:
            samples_to_process = ["SAMPLE_001"]  # Single-sample VCF fallback name

        for site in sites:
            # Filter VCF records matching this site position
            c_chrom = harmonize_contig(site.chrom, target_has_chr=True)
            site_recs = [r for r in vcf_records if r.chrom == c_chrom and r.pos == site.pos]

            for sid in samples_to_process:
                status = SiteObservationStatus.NOT_IN_VCF
                ref_ev = ReferenceEvidence.NONE
                gt_str = None
                allele1 = None
                allele2 = None
                phased = False
                dp = None
                gq = None
                vcf_fltr = None
                matched_alt = None

                if not site_recs:
                    # Site absent from VCF -> check callable evidence
                    is_callable, ev_type = evaluate_callable_evidence(
                        site.chrom, site.pos, vcf_records, sample_id=sid, bed_intervals=bed_intervals
                    )
                    if is_callable:
                        status = SiteObservationStatus.HOM_REF
                        ref_ev = ev_type
                        gt_str = "0/0"
                        allele1, allele2 = 0, 0
                    else:
                        status = SiteObservationStatus.NOT_IN_VCF
                        ref_ev = ReferenceEvidence.NONE
                else:
                    # VCF record exists at this position
                    matched_rec = site_recs[0]
                    vcf_fltr = matched_rec.filter
                    
                    if sid in matched_rec.genotypes:
                        gt_obj = matched_rec.genotypes[sid]
                        gt_str = gt_obj.gt_str
                        allele1 = gt_obj.allele1
                        allele2 = gt_obj.allele2
                        phased = gt_obj.phased
                        dp = gt_obj.dp
                        gq = gt_obj.gq

                    # Check NO_CALL
                    if gt_str in ["./.", ".|.", ".", None] or (allele1 is None and allele2 is None):
                        status = SiteObservationStatus.NO_CALL
                        ref_ev = ReferenceEvidence.NONE
                    else:
                        # Normalize record alleles and match against catalogued site
                        norm_chr, norm_pos, norm_ref, norm_alt = normalize_variant(
                            matched_rec.chrom, matched_rec.pos, matched_rec.ref,
                            matched_rec.alts[0] if matched_rec.alts else site.ref
                        )

                        # Determine call from allele indices
                        if allele1 == 0 and allele2 == 0:
                            status = SiteObservationStatus.HOM_REF
                            ref_ev = ReferenceEvidence.EXPLICIT_GT
                        elif allele1 == 1 and allele2 == 1:
                            status = SiteObservationStatus.HOM_ALT
                            ref_ev = ReferenceEvidence.NONE
                            matched_alt = site.alt
                        elif (allele1 == 0 and allele2 == 1) or (allele1 == 1 and allele2 == 0):
                            status = SiteObservationStatus.HET
                            ref_ev = ReferenceEvidence.NONE
                            matched_alt = site.alt
                        elif allele1 is not None and allele1 > 1 or allele2 is not None and allele2 > 1:
                            status = SiteObservationStatus.MULTIALLELIC
                            ref_ev = ReferenceEvidence.NONE

                        # Check if alternate allele matches catalogued alt
                        if matched_rec.alts and site.alt not in matched_rec.alts and status in [SiteObservationStatus.HET, SiteObservationStatus.HOM_ALT]:
                            status = SiteObservationStatus.MULTIALLELIC

                        # Apply QC filter & DP/GQ threshold checks
                        override_status, filter_reason = apply_genotype_qc(vcf_fltr, dp, gq, qc_config)
                        if override_status is not None:
                            status = override_status
                            if filter_reason != "PASS":
                                vcf_fltr = filter_reason

                # Build site_calls row
                all_rows.append({
                    "sample_id": sid,
                    "gene": site.gene,
                    "site_id": site.site_id,
                    "chrom": site.chrom,
                    "pos": site.pos,
                    "ref": site.ref,
                    "alt": site.alt,
                    "gt": gt_str,
                    "allele1": allele1,
                    "allele2": allele2,
                    "status": status.value if isinstance(status, SiteObservationStatus) else str(status),
                    "reference_evidence": ref_ev.value if isinstance(ref_ev, ReferenceEvidence) else str(ref_ev),
                    "phased": phased,
                    "dp": dp,
                    "gq": gq,
                    "filter": vcf_fltr,
                    "role": site.role,
                    "provenance_class": provenance_class,
                    "source_file_sha256": source_sha256,
                    "schema_version": schema_version
                })

    df = pd.DataFrame(all_rows)

    # PROPERTY ASSERTION CHECK: Zero rows with HOM_REF and reference_evidence == none
    invalid_mask = (df["status"] == SiteObservationStatus.HOM_REF.value) & (df["reference_evidence"] == ReferenceEvidence.NONE.value)
    if invalid_mask.any():
        invalid_count = invalid_mask.sum()
        raise ValueError(
            f"PROPERTY ASSERTION FAILURE: Found {invalid_count} rows with status=HOM_REF and reference_evidence=none. "
            f"Missing sites must never be classified as HOM_REF without supporting evidence."
        )

    return df
