from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any


from backend.genomics.enums import ReferenceEvidence
from backend.genomics.normalize import harmonize_contig


def parse_bed_file(bed_path: Union[str, Path]) -> Dict[str, List[Tuple[int, int]]]:
    """
    Parses a 3-column BED file into interval lists per chromosome.
    BED intervals are 0-based half-open [start, end).
    """
    intervals: Dict[str, List[Tuple[int, int]]] = {}
    path = Path(bed_path)
    if not path.is_file():
        return intervals

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("track") or line.startswith("browser"):
                continue
            cols = line.split("\t")
            if len(cols) >= 3:
                chrom = harmonize_contig(cols[0], target_has_chr=True)
                try:
                    start_0 = int(cols[1])
                    end_0 = int(cols[2])
                    intervals.setdefault(chrom, []).append((start_0, end_0))
                except ValueError:
                    continue
    return intervals


def is_pos_in_bed_intervals(chrom: str, pos_1based: int, bed_intervals: Dict[str, List[Tuple[int, int]]]) -> bool:
    """
    Checks if 1-based position is covered by BED intervals.
    """
    c_chrom = harmonize_contig(chrom, target_has_chr=True)
    pos_0based = pos_1based - 1
    for start_0, end_0 in bed_intervals.get(c_chrom, []):
        if start_0 <= pos_0based < end_0:
            return True
    return False


def evaluate_callable_evidence(
    chrom: str,
    pos: int,
    records: List[Any],
    sample_id: Optional[str] = None,
    bed_intervals: Optional[Dict[str, List[Tuple[int, int]]]] = None
) -> Tuple[bool, ReferenceEvidence]:
    """
    Evaluates supporting reference evidence for an unobserved or non-variant site.

    Args:
        chrom (str): Target chromosome.
        pos (int): 1-based target position.
        records (List[VcfRecord]): VCF records overlapping position.
        sample_id (str | None): Sample identifier.
        bed_intervals (Dict | None): Parsed BED intervals.

    Returns:
        Tuple[bool, ReferenceEvidence]: (is_callable, reference_evidence)
    """
    # 1. Check user-supplied callable BED
    if bed_intervals and is_pos_in_bed_intervals(chrom, pos, bed_intervals):
        return True, ReferenceEvidence.CALLABLE_BED

    # 2. Check for gVCF reference block record overlapping pos
    c_chrom = harmonize_contig(chrom, target_has_chr=True)
    for rec in records:
        if rec.chrom == c_chrom:
            end_pos = rec.pos
            if "END" in rec.info:
                try:
                    end_pos = int(rec.info["END"])
                except ValueError:
                    end_pos = rec.pos

            if rec.pos <= pos <= end_pos:
                # Check sample genotype in gVCF block
                if sample_id and sample_id in rec.genotypes:
                    gt_obj = rec.genotypes[sample_id]
                    if gt_obj.gt_str in ["0/0", "0|0"]:
                        return True, ReferenceEvidence.GVCF_BLOCK
                elif not rec.genotypes or not sample_id:
                    return True, ReferenceEvidence.GVCF_BLOCK

    return False, ReferenceEvidence.NONE
