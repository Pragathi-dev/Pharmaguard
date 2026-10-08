"""
Main Entry Point for GeneWeave-Risk Pharmacogenomic (PGx) Pipeline.
Integrates VCF Reading, Star Allele Calling, Diplotype Assignment, and CPIC Phenotyping.
"""

from typing import Dict, List, Optional
from backend.pgx.data_model import SampleGeneInterpretation, VariantCall
from backend.pgx.vcf_reader import VCFReader
from backend.pgx.gene_interpreters import (
    CYP2C19Interpreter, CYP2C9Interpreter, DPYDInterpreter,
    SLCO1B1Interpreter, CYP2D6Interpreter
)


class PharmacogenomicPipeline:
    """Orchestrates VCF reading, gene-level star-allele calling, and CPIC phenotyping."""

    GENE_CHROMOSOME_WINDOWS = {
        "CYP2C19": {"chrom": "10", "start": 94000000, "end": 97000000},
        "CYP2C9": {"chrom": "10", "start": 94000000, "end": 97000000},
        "DPYD": {"chrom": "1", "start": 97000000, "end": 99000000},
        "SLCO1B1": {"chrom": "12", "start": 21000000, "end": 22000000},
        "CYP2D6": {"chrom": "22", "start": 42000000, "end": 43000000},
    }

    def __init__(self):
        self.interpreters = {
            "CYP2C19": CYP2C19Interpreter(),
            "CYP2C9": CYP2C9Interpreter(),
            "DPYD": DPYDInterpreter(),
            "SLCO1B1": SLCO1B1Interpreter(),
            "CYP2D6": CYP2D6Interpreter(),
        }

    def analyze_vcf_for_sample(
        self,
        vcf_file_path: str,
        target_sample_id: Optional[str] = None
    ) -> Dict[str, SampleGeneInterpretation]:
        """
        Extracts sample variants across windows and calls diplotype/phenotype.
        """
        reader = VCFReader(vcf_file_path)
        results: Dict[str, SampleGeneInterpretation] = {}

        for gene_name, interpreter in self.interpreters.items():
            window = self.GENE_CHROMOSOME_WINDOWS.get(gene_name, {})
            variants, sample_id, total_ex = reader.extract_sample_variants(
                target_sample_id=target_sample_id,
                chrom_filter=window.get("chrom"),
                start_pos=window.get("start"),
                end_pos=window.get("end"),
                gene_name=gene_name
            )

            active_sample_id = target_sample_id or sample_id or "UNKNOWN"
            gene_result = interpreter.interpret(active_sample_id, variants, total_ex)
            results[gene_name] = gene_result

        return results
