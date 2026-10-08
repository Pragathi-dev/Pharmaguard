"""
Fast and Robust VCF Parser for Pharmacogenomic Variant Extractions.
Supports plain VCF and gzipped VCF (.vcf.gz), single-sample and multi-sample files.
"""

import gzip
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
from backend.pgx.data_model import VariantCall


class VCFReader:
    """Reads VCF files and extracts normalized VariantCall objects."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"VCF file not found: {self.filepath}")

    def _open_file(self):
        if str(self.filepath).endswith('.gz'):
            return gzip.open(self.filepath, 'rt', encoding='utf-8', errors='replace')
        return open(self.filepath, 'r', encoding='utf-8', errors='replace')

    def get_available_samples(self) -> List[str]:
        """Returns the list of sample IDs present in the VCF header."""
        samples = []
        with self._open_file() as f:
            for line in f:
                if line.startswith('#CHROM'):
                    cols = line.strip().split('\t')
                    if len(cols) > 9:
                        samples = cols[9:]
                    break
        return samples

    def extract_sample_variants(
        self,
        target_sample_id: Optional[str] = None,
        chrom_filter: Optional[str] = None,
        start_pos: Optional[int] = None,
        end_pos: Optional[int] = None,
        gene_name: Optional[str] = None
    ) -> Tuple[List[VariantCall], str, int]:
        """
        Extracts non-wildtype variant calls for a given sample ID.
        Returns: (variant_calls_list, selected_sample_id, total_records_examined)
        """
        available_samples = self.get_available_samples()
        selected_sample_id = "SAMPLE"
        sample_col_idx = 9

        if available_samples:
            if target_sample_id and target_sample_id in available_samples:
                selected_sample_id = target_sample_id
                sample_col_idx = available_samples.index(target_sample_id) + 9
            else:
                selected_sample_id = available_samples[0]
                sample_col_idx = 9

        variant_calls: List[VariantCall] = []
        total_records_examined = 0

        # Standardize chromosome filter naming (e.g. "chr10" vs "10")
        target_chroms: Set[str] = set()
        if chrom_filter:
            clean_chr = str(chrom_filter).replace('chr', '')
            target_chroms = {clean_chr, f"chr{clean_chr}"}

        with self._open_file() as f:
            for line in f:
                if line.startswith('#'):
                    continue

                cols = line.strip().split('\t')
                if len(cols) < 8:
                    continue

                chrom = cols[0]
                if target_chroms and chrom not in target_chroms:
                    continue

                try:
                    pos = int(cols[1])
                except ValueError:
                    continue

                if start_pos and pos < start_pos:
                    continue
                if end_pos and pos > end_pos:
                    continue

                total_records_examined += 1

                rsid = cols[2] if cols[2] != '.' else None
                ref = cols[3]
                alt = cols[4]

                try:
                    qual = float(cols[5]) if cols[5] != '.' else None
                except ValueError:
                    qual = None

                # Extract GT from sample column
                genotype = "./."
                is_phased = False

                if len(cols) > sample_col_idx:
                    format_fields = cols[8].split(':')
                    sample_fields = cols[sample_col_idx].split(':')

                    if 'GT' in format_fields:
                        gt_idx = format_fields.index('GT')
                        if gt_idx < len(sample_fields):
                            genotype = sample_fields[gt_idx]
                    else:
                        genotype = sample_fields[0]

                # Filter out wildtype (0/0, 0|0) and missing (./., .)
                if genotype in ['0/0', '0|0', './.', '.', '0']:
                    continue

                if '|' in genotype:
                    is_phased = True

                vc = VariantCall(
                    sample_id=selected_sample_id,
                    gene=gene_name or "UNKNOWN",
                    chrom=chrom.replace('chr', ''),
                    pos=pos,
                    ref=ref,
                    alt=alt,
                    genotype=genotype,
                    rsid=rsid,
                    is_phased=is_phased,
                    quality=qual
                )
                variant_calls.append(vc)

        return variant_calls, selected_sample_id, total_records_examined

    def extract_all_samples_variants(
        self,
        chrom_filter: Optional[str] = None,
        start_pos: Optional[int] = None,
        end_pos: Optional[int] = None,
        target_positions: Optional[Set[int]] = None,
        target_rsids: Optional[Set[str]] = None,
        gene_name: Optional[str] = None
    ) -> Tuple[Dict[str, List[VariantCall]], int]:
        """
        Extracts variant calls for ALL samples in a multi-sample VCF in a SINGLE file pass.
        Returns: (sample_variants_dict, total_records_examined)
        """
        available_samples = self.get_available_samples()
        sample_variants: Dict[str, List[VariantCall]] = {s: [] for s in available_samples}
        total_records_examined = 0

        target_chroms: Set[str] = set()
        if chrom_filter:
            clean_chr = str(chrom_filter).replace('chr', '')
            target_chroms = {clean_chr, f"chr{clean_chr}"}

        with self._open_file() as f:
            for line in f:
                if line.startswith('#'):
                    continue

                cols = line.strip().split('\t')
                if len(cols) < 9:
                    continue

                chrom = cols[0]
                if target_chroms and chrom not in target_chroms:
                    continue

                try:
                    pos = int(cols[1])
                except ValueError:
                    continue

                if start_pos and pos < start_pos:
                    continue
                if end_pos and pos > end_pos:
                    continue

                rsid = cols[2] if cols[2] != '.' else None

                # Instant position / rsid filter if provided
                if target_positions and pos not in target_positions:
                    if not (target_rsids and rsid and rsid in target_rsids):
                        continue

                total_records_examined += 1

                ref = cols[3]
                alt = cols[4]

                try:
                    qual = float(cols[5]) if cols[5] != '.' else None
                except ValueError:
                    qual = None

                format_fields = cols[8].split(':')
                gt_idx = format_fields.index('GT') if 'GT' in format_fields else 0

                # Iterate across all sample columns for matching target variants
                for i, sample_id in enumerate(available_samples):
                    col_idx = 9 + i
                    if col_idx >= len(cols):
                        break

                    sample_fields = cols[col_idx].split(':')
                    genotype = sample_fields[gt_idx] if gt_idx < len(sample_fields) else sample_fields[0]

                    if genotype in ['0/0', '0|0', './.', '.', '0']:
                        continue

                    is_phased = '|' in genotype

                    vc = VariantCall(
                        sample_id=sample_id,
                        gene=gene_name or "UNKNOWN",
                        chrom=chrom.replace('chr', ''),
                        pos=pos,
                        ref=ref,
                        alt=alt,
                        genotype=genotype,
                        rsid=rsid,
                        is_phased=is_phased,
                        quality=qual
                    )
                    sample_variants[sample_id].append(vc)

        return sample_variants, total_records_examined

