import gzip
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from backend.common.logging_config import get_logger
from backend.genomics.normalize import harmonize_contig

logger = get_logger("pharmaguard.genomics.vcf_reader")


@dataclass
class GenotypeData:
    sample_id: str
    gt_str: str          # e.g., "0/1", "1|1", "./."
    allele1: Optional[int]
    allele2: Optional[int]
    phased: bool
    dp: Optional[int]
    gq: Optional[int]


@dataclass
class VcfRecord:
    chrom: str
    pos: int
    id: str
    ref: str
    alts: List[str]
    qual: Optional[float]
    filter: str
    info: Dict[str, Any]
    genotypes: Dict[str, GenotypeData] = field(default_factory=dict)
    line_number: Optional[int] = None


def parse_vcf_line(
    line: str,
    samples: List[str],
    line_num: int
) -> Optional[VcfRecord]:
    """
    Parses a single non-header VCF data line.
    Skips malformed lines gracefully without crashing.

    Args:
        line (str): Raw VCF line text.
        samples (List[str]): List of sample column names from #CHROM header.
        line_num (int): Line number for error logging.

    Returns:
        Optional[VcfRecord]: Parsed record or None if malformed.
    """
    cols = line.strip().split("\t")
    if len(cols) < 8:
        logger.warning(f"Malformed VCF line {line_num}: insufficient columns ({len(cols)} < 8)")
        return None

    try:
        chrom = harmonize_contig(cols[0], target_has_chr=True)
        pos = int(cols[1])
        rsid = cols[2]
        ref = cols[3].upper().strip()
        alts = [a.upper().strip() for a in cols[4].split(",")] if cols[4] != "." else []
        
        try:
            qual = float(cols[5]) if cols[5] != "." else None
        except ValueError:
            qual = None

        fltr = cols[6]

        info_dict = {}
        if cols[7] != ".":
            for item in cols[7].split(";"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    info_dict[k] = v
                else:
                    info_dict[item] = True

        genotypes = {}
        if len(cols) >= 9 and len(samples) > 0:
            format_keys = cols[8].split(":")
            gt_idx = format_keys.index("GT") if "GT" in format_keys else 0
            dp_idx = format_keys.index("DP") if "DP" in format_keys else None
            gq_idx = format_keys.index("GQ") if "GQ" in format_keys else None

            for i, sname in enumerate(samples):
                col_idx = 9 + i
                if col_idx < len(cols):
                    sample_str = cols[col_idx]
                    s_vals = sample_str.split(":")
                    
                    raw_gt = s_vals[gt_idx] if gt_idx < len(s_vals) else "./."
                    phased = "|" in raw_gt
                    
                    # Parse alleles
                    clean_gt = raw_gt.replace("|", "/")
                    parts = clean_gt.split("/")
                    a1 = int(parts[0]) if len(parts) > 0 and parts[0] not in [".", "?"] else None
                    a2 = int(parts[1]) if len(parts) > 1 and parts[1] not in [".", "?"] else a1

                    dp = None
                    if dp_idx is not None and dp_idx < len(s_vals):
                        try:
                            dp = int(s_vals[dp_idx])
                        except ValueError:
                            dp = None

                    gq = None
                    if gq_idx is not None and gq_idx < len(s_vals):
                        try:
                            gq = int(float(s_vals[gq_idx]))
                        except ValueError:
                            gq = None

                    genotypes[sname] = GenotypeData(
                        sample_id=sname,
                        gt_str=raw_gt,
                        allele1=a1,
                        allele2=a2,
                        phased=phased,
                        dp=dp,
                        gq=gq
                    )

        return VcfRecord(
            chrom=chrom,
            pos=pos,
            id=rsid,
            ref=ref,
            alts=alts,
            qual=qual,
            filter=fltr,
            info=info_dict,
            genotypes=genotypes,
            line_number=line_num
        )

    except Exception as exc:
        logger.warning(f"Skipped malformed VCF line {line_num}: {exc}")
        return None


def read_vcf_records(
    vcf_path: Union[str, Path],
    region_chrom: Optional[str] = None,
    region_start: Optional[int] = None,
    region_end: Optional[int] = None
) -> Tuple[List[VcfRecord], List[str], int]:
    """
    Reads VCF records from file (handles plain VCF and gzipped VCF).
    Skips malformed records gracefully and logs line numbers.

    Args:
        vcf_path (str | Path): Path to VCF file.
        region_chrom (str | None): Optional target chromosome filter.
        region_start (int | None): Optional 1-based start position filter.
        region_end (int | None): Optional 1-based end position filter.

    Returns:
        Tuple[List[VcfRecord], List[str], int]: (records, samples_list, malformed_count)
    """
    file_path = Path(vcf_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"VCF file not found: {file_path}")

    target_chr_norm = harmonize_contig(region_chrom, target_has_chr=True) if region_chrom else None

    # Open gzip or text stream
    is_gz = file_path.suffix == ".gz" or str(file_path).endswith(".vcf.gz")
    open_fn = lambda: gzip.open(file_path, "rt", encoding="utf-8") if is_gz else open(file_path, "r", encoding="utf-8")

    records = []
    samples = []
    malformed_count = 0
    line_num = 0

    with open_fn() as f:
        for line in f:
            line_num += 1
            if line.startswith("#"):
                if line.startswith("#CHROM"):
                    cols = line.strip().split("\t")
                    if len(cols) > 9:
                        samples = cols[9:]
                continue

            # Quick position filtering if region provided
            rec = parse_vcf_line(line, samples, line_num)
            if rec is None:
                malformed_count += 1
                continue

            if target_chr_norm and rec.chrom != target_chr_norm:
                continue

            if region_start and rec.pos < region_start:
                continue

            if region_end and rec.pos > region_end:
                continue

            records.append(rec)

    logger.info(f"Read {len(records)} VCF records from {file_path.name} (samples: {len(samples)}, malformed skipped: {malformed_count})")
    return records, samples, malformed_count
