from typing import Tuple


def harmonize_contig(chrom: str, target_has_chr: bool = True) -> str:
    """
    Harmonizes contig names between 'chr10' and '10' representations.

    Args:
        chrom (str): Input chromosome string.
        target_has_chr (bool): Whether the output should include 'chr' prefix.

    Returns:
        str: Harmonized contig name.
    """
    clean_chrom = str(chrom).strip()
    if clean_chrom.startswith("chr"):
        raw_num = clean_chrom[3:]
    else:
        raw_num = clean_chrom

    if target_has_chr:
        return f"chr{raw_num}"
    return raw_num


def normalize_variant(
    chrom: str,
    pos: int,
    ref: str,
    alt: str
) -> Tuple[str, int, str, str]:
    """
    Trims common leading and trailing bases from REF and ALT alleles (left-alignment).

    Args:
        chrom (str): Chromosome name.
        pos (int): 1-based start position.
        ref (str): Reference allele.
        alt (str): Alternate allele.

    Returns:
        Tuple[str, int, str, str]: (chrom, pos, ref, alt) normalized.
    """
    c_chrom = harmonize_contig(chrom, target_has_chr=True)
    c_ref = ref.upper().strip()
    c_alt = alt.upper().strip()
    c_pos = pos

    # Trim common right suffix if either allele length > 1
    while len(c_ref) > 1 and len(c_alt) > 1 and c_ref[-1] == c_alt[-1]:
        c_ref = c_ref[:-1]
        c_alt = c_alt[:-1]

    # Trim common left prefix if both share initial base
    while len(c_ref) > 0 and len(c_alt) > 0 and c_ref[0] == c_alt[0] and (len(c_ref) > 1 or len(c_alt) > 1):
        c_ref = c_ref[1:]
        c_alt = c_alt[1:]
        c_pos += 1

    return c_chrom, c_pos, c_ref, c_alt
