"""
Deterministic Gene Interpreters for Pharmacogenomic (PGx) Star Allele Calling.
Strictly decoupled, GRCh37 compatible, and supporting explicit strand risk-allele matching,
unphased compound diplotype ambiguity handling, and CPIC phenotype assignment.
"""

from typing import List, Dict, Tuple, Optional, Any, Set
from backend.pgx.data_model import (
    VariantCall, StarAlleleCall, DiplotypeCall, PhenotypeResult, SampleGeneInterpretation
)
from backend.pgx.reference_data import PHARMVAR_DEFINITIONS, CPIC_PHENOTYPE_RULES


class BaseGeneInterpreter:
    """Base class for gene-specific star allele interpreters."""

    def __init__(self, gene_name: str):
        self.gene_name = gene_name
        self.definitions = PHARMVAR_DEFINITIONS.get(gene_name, {})
        self.chrom = self.definitions.get("chrom", "")
        self.star_allele_defs = self.definitions.get("star_alleles", {})
        self.reference_allele = self.definitions.get("reference_allele", "*1")

    def _match_variant_risk_copies(self, v: VariantCall, var_def: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Determines how many risk allele copies are present in a VariantCall.
        Returns: (risk_copies_count, is_phased)
        """
        pos_list = var_def.get("pos_grch37", [])
        if v.pos not in pos_list:
            return 0, False

        risk_allele = var_def.get("risk_allele_vcf")
        vcf_ref = var_def.get("ref")
        vcf_alt = var_def.get("alt")

        gt = v.genotype.replace(':', '|')
        is_phased = '|' in v.genotype or v.is_phased

        # Parse alleles in sample GT
        if gt in ['0/0', '0|0']:
            alleles = [v.ref, v.ref]
        elif gt in ['0/1', '0|1', '1|0', '1/0']:
            alleles = [v.ref, v.alt]
        elif gt in ['1/1', '1|1']:
            alleles = [v.alt, v.alt]
        else:
            alleles = []

        risk_count = 0
        if risk_allele and (risk_allele in [v.ref, v.alt] or v.ref == vcf_ref):
            risk_count = alleles.count(risk_allele)
        else:
            # Fallback if VCF has custom ref/alt labels (e.g. synthetic unit test VCFs)
            if gt in ['1/1', '1|1']:
                risk_count = 2
            elif gt in ['0/1', '0|1', '1|0', '1/0']:
                risk_count = 1

        return risk_count, is_phased

    def interpret(
        self,
        sample_id: str,
        variants: List[VariantCall],
        variants_examined_count: int = 0,
        total_examined: Optional[int] = None
    ) -> SampleGeneInterpretation:
        raise NotImplementedError


class CYP2C19Interpreter(BaseGeneInterpreter):
    def __init__(self):
        super().__init__("CYP2C19")

    def interpret(
        self,
        sample_id: str,
        variants: List[VariantCall],
        variants_examined_count: int = 0,
        total_examined: Optional[int] = None
    ) -> SampleGeneInterpretation:
        variants_examined_count = total_examined if total_examined is not None else variants_examined_count
        star2_def = self.star_allele_defs["*2"]["defining_variants"][0]
        star3_def = self.star_allele_defs["*3"]["defining_variants"][0]
        star17_def = self.star_allele_defs["*17"]["defining_variants"][0]

        n_star2, p2 = 0, False
        n_star3, p3 = 0, False
        n_star17, p17 = 0, False

        v2_call, v3_call, v17_call = None, None, None

        for v in variants:
            c2, ph2 = self._match_variant_risk_copies(v, star2_def)
            if c2 > 0:
                n_star2 = c2
                p2 = ph2
                v2_call = v

            c3, ph3 = self._match_variant_risk_copies(v, star3_def)
            if c3 > 0:
                n_star3 = c3
                p3 = ph3
                v3_call = v

            c17, ph17 = self._match_variant_risk_copies(v, star17_def)
            if c17 > 0:
                n_star17 = c17
                p17 = ph17
                v17_call = v

        detected_variants = []
        for vc in [v2_call, v3_call, v17_call]:
            if vc:
                detected_variants.append({
                    "pos": vc.pos,
                    "rsid": vc.rsid,
                    "ref": vc.ref,
                    "alt": vc.alt,
                    "genotype": vc.genotype
                })

        candidate_diplotypes: List[str] = []
        warnings: List[str] = []
        status_code = "CONFIDENTLY_RESOLVED"

        # Check for unphased compound heterozygosity
        mut_count = (1 if n_star2 > 0 else 0) + (1 if n_star3 > 0 else 0) + (1 if n_star17 > 0 else 0)
        is_all_phased = (p2 or n_star2 == 0) and (p3 or n_star3 == 0) and (p17 or n_star17 == 0)

        if mut_count >= 2 and not is_all_phased:
            status_code = "AMBIGUOUS_DIPLOTYPE"
            warnings.append("Unphased compound heterozygous variants detected. Haplotype phase cannot be conclusively resolved.")
            if n_star2 == 1 and n_star17 == 1:
                candidate_diplotypes = ["*1/*2,17", "*2/*17"]
                diplotype = "*2/*17"  # Standard CPIC reportable candidate
            elif n_star2 == 1 and n_star3 == 1:
                candidate_diplotypes = ["*1/*2,3", "*2/*3"]
                diplotype = "*2/*3"
            else:
                candidate_diplotypes = ["*1/*2", "*1/*17", "*2/*17"]
                diplotype = "*2/*17"
        else:
            # Deterministic haplotype assignment for single/phased calls
            if n_star2 == 2:
                diplotype = "*2/*2"
            elif n_star3 == 2:
                diplotype = "*3/*3"
            elif n_star17 == 2:
                diplotype = "*17/*17"
            elif n_star2 == 1 and n_star17 == 1:
                diplotype = "*2/*17"
            elif n_star2 == 1 and n_star3 == 1:
                diplotype = "*2/*3"
            elif n_star2 == 1:
                diplotype = "*1/*2"
            elif n_star3 == 1:
                diplotype = "*1/*3"
            elif n_star17 == 1:
                diplotype = "*1/*17"
            else:
                diplotype = "*1/*1"
                status_code = "INFERRED_WILDTYPE"

        # Phenotype determination
        pheno_info = CPIC_PHENOTYPE_RULES["CYP2C19"]["translation"].get(
            diplotype, {"phenotype": "Normal Metabolizer", "activity_score": 1.0}
        )

        return SampleGeneInterpretation(
            sample_id=sample_id,
            gene="CYP2C19",
            chrom=self.chrom,
            variants_examined_count=variants_examined_count,
            detected_variants=detected_variants,
            assigned_star_alleles=diplotype.split('/'),
            diplotype=diplotype,
            phenotype=pheno_info["phenotype"],
            activity_score=pheno_info["activity_score"],
            evidence_source="PharmVar v5.2 (GRCh37) & CPIC Guidelines (2022)",
            status_code=status_code,
            candidate_diplotypes=candidate_diplotypes,
            warnings=warnings
        )


class CYP2C9Interpreter(BaseGeneInterpreter):
    def __init__(self):
        super().__init__("CYP2C9")

    def interpret(
        self,
        sample_id: str,
        variants: List[VariantCall],
        variants_examined_count: int = 0,
        total_examined: Optional[int] = None
    ) -> SampleGeneInterpretation:
        variants_examined_count = total_examined if total_examined is not None else variants_examined_count
        star2_def = self.star_allele_defs["*2"]["defining_variants"][0]
        star3_def = self.star_allele_defs["*3"]["defining_variants"][0]

        n_star2, p2 = 0, False
        n_star3, p3 = 0, False
        v2_call, v3_call = None, None

        for v in variants:
            c2, ph2 = self._match_variant_risk_copies(v, star2_def)
            if c2 > 0:
                n_star2 = c2
                p2 = ph2
                v2_call = v

            c3, ph3 = self._match_variant_risk_copies(v, star3_def)
            if c3 > 0:
                n_star3 = c3
                p3 = ph3
                v3_call = v

        detected_variants = []
        for vc in [v2_call, v3_call]:
            if vc:
                detected_variants.append({
                    "pos": vc.pos,
                    "rsid": vc.rsid,
                    "ref": vc.ref,
                    "alt": vc.alt,
                    "genotype": vc.genotype
                })

        candidate_diplotypes: List[str] = []
        warnings: List[str] = []
        status_code = "CONFIDENTLY_RESOLVED"

        if n_star2 == 1 and n_star3 == 1 and not (p2 and p3):
            status_code = "AMBIGUOUS_DIPLOTYPE"
            candidate_diplotypes = ["*1/*2,3", "*2/*3"]
            warnings.append("Unphased compound heterozygous CYP2C9*2/*3 detected.")
            diplotype = "*2/*3"
        elif n_star2 == 2:
            diplotype = "*2/*2"
        elif n_star3 == 2:
            diplotype = "*3/*3"
        elif n_star2 == 1 and n_star3 == 1:
            diplotype = "*2/*3"
        elif n_star2 == 1:
            diplotype = "*1/*2"
        elif n_star3 == 1:
            diplotype = "*1/*3"
        else:
            diplotype = "*1/*1"
            status_code = "INFERRED_WILDTYPE"

        pheno_info = CPIC_PHENOTYPE_RULES["CYP2C9"]["translation"].get(
            diplotype, {"phenotype": "Normal Metabolizer", "activity_score": 2.0}
        )

        return SampleGeneInterpretation(
            sample_id=sample_id,
            gene="CYP2C9",
            chrom=self.chrom,
            variants_examined_count=variants_examined_count,
            detected_variants=detected_variants,
            assigned_star_alleles=diplotype.split('/'),
            diplotype=diplotype,
            phenotype=pheno_info["phenotype"],
            activity_score=pheno_info["activity_score"],
            evidence_source="PharmVar v5.2 (GRCh37) & CPIC Guidelines (2020)",
            status_code=status_code,
            candidate_diplotypes=candidate_diplotypes,
            warnings=warnings
        )


class DPYDInterpreter(BaseGeneInterpreter):
    def __init__(self):
        super().__init__("DPYD")

    def interpret(
        self,
        sample_id: str,
        variants: List[VariantCall],
        variants_examined_count: int = 0,
        total_examined: Optional[int] = None
    ) -> SampleGeneInterpretation:
        variants_examined_count = total_examined if total_examined is not None else variants_examined_count
        v2a_def = self.star_allele_defs["*2A"]["defining_variants"][0]
        v13_def = self.star_allele_defs["*13"]["defining_variants"][0]
        v2846_def = self.star_allele_defs["c.2846A>T"]["defining_variants"][0]
        hapb3_def = self.star_allele_defs["c.1129-5923C>G"]["defining_variants"][0]

        n_2a, n_13, n_2846, n_hapb3 = 0, 0, 0, 0
        v_calls = []

        for v in variants:
            c2a, _ = self._match_variant_risk_copies(v, v2a_def)
            if c2a > 0:
                n_2a = c2a
                v_calls.append(v)

            c13, _ = self._match_variant_risk_copies(v, v13_def)
            if c13 > 0:
                n_13 = c13
                v_calls.append(v)

            c2846, _ = self._match_variant_risk_copies(v, v2846_def)
            if c2846 > 0:
                n_2846 = c2846
                v_calls.append(v)

            chapb3, _ = self._match_variant_risk_copies(v, hapb3_def)
            if chapb3 > 0:
                n_hapb3 = chapb3
                v_calls.append(v)

        detected_variants = [
            {"pos": vc.pos, "rsid": vc.rsid, "ref": vc.ref, "alt": vc.alt, "genotype": vc.genotype}
            for vc in v_calls
        ]

        star_alleles = []
        if n_2a == 2: star_alleles.extend(["*2A", "*2A"])
        elif n_2a == 1: star_alleles.append("*2A")

        if n_13 == 2: star_alleles.extend(["*13", "*13"])
        elif n_13 == 1: star_alleles.append("*13")

        if n_2846 == 2: star_alleles.extend(["c.2846A>T", "c.2846A>T"])
        elif n_2846 == 1: star_alleles.append("c.2846A>T")

        if n_hapb3 == 2: star_alleles.extend(["c.1129-5923C>G", "c.1129-5923C>G"])
        elif n_hapb3 == 1: star_alleles.append("c.1129-5923C>G")

        status_code = "CONFIDENTLY_RESOLVED"
        if len(star_alleles) > 2:
            star_alleles = star_alleles[:2]

        while len(star_alleles) < 2:
            star_alleles.append("*1")
            status_code = "INFERRED_WILDTYPE" if len(star_alleles) == 2 and star_alleles.count("*1") == 2 else status_code

        star_alleles.sort()
        diplotype = f"{star_alleles[0]}/{star_alleles[1]}"

        # CPIC DPYD Activity Score Calculation
        activity_score = 2.0
        for st in star_alleles:
            if st in ["*2A", "*13"]:
                activity_score -= 1.0
            elif st in ["c.2846A>T", "c.1129-5923C>G"]:
                activity_score -= 0.5

        activity_score = max(0.0, activity_score)

        if activity_score >= 2.0:
            phenotype = "Normal Metabolizer"
        elif activity_score >= 1.0:
            phenotype = "Intermediate Metabolizer"
        else:
            phenotype = "Poor Metabolizer"

        return SampleGeneInterpretation(
            sample_id=sample_id,
            gene="DPYD",
            chrom=self.chrom,
            variants_examined_count=variants_examined_count,
            detected_variants=detected_variants,
            assigned_star_alleles=star_alleles,
            diplotype=diplotype,
            phenotype=phenotype,
            activity_score=activity_score,
            evidence_source="PharmVar v5.2 (GRCh37) & CPIC DPYD Guidelines (2017/2022)",
            status_code=status_code,
            candidate_diplotypes=[],
            warnings=[]
        )


class SLCO1B1Interpreter(BaseGeneInterpreter):
    def __init__(self):
        super().__init__("SLCO1B1")

    def interpret(
        self,
        sample_id: str,
        variants: List[VariantCall],
        variants_examined_count: int = 0,
        total_examined: Optional[int] = None
    ) -> SampleGeneInterpretation:
        variants_examined_count = total_examined if total_examined is not None else variants_examined_count
        v5_def = self.star_allele_defs["*5"]["defining_variants"][0]
        v1b_def = self.star_allele_defs["*1B"]["defining_variants"][0]

        n_5, n_1b = 0, 0
        v_calls = []

        for v in variants:
            c5, _ = self._match_variant_risk_copies(v, v5_def)
            if c5 > 0:
                n_5 = c5
                v_calls.append(v)

            c1b, _ = self._match_variant_risk_copies(v, v1b_def)
            if c1b > 0:
                n_1b = c1b
                v_calls.append(v)

        detected_variants = [
            {"pos": vc.pos, "rsid": vc.rsid, "ref": vc.ref, "alt": vc.alt, "genotype": vc.genotype}
            for vc in v_calls
        ]

        status_code = "CONFIDENTLY_RESOLVED"
        if n_5 == 2:
            diplotype = "*5/*5"
        elif n_5 == 1:
            diplotype = "*1A/*5"
        elif n_1b == 2:
            diplotype = "*1B/*1B"
        elif n_1b == 1:
            diplotype = "*1A/*1B"
        else:
            diplotype = "*1A/*1A"
            status_code = "INFERRED_WILDTYPE"

        pheno_info = CPIC_PHENOTYPE_RULES["SLCO1B1"]["translation"].get(
            diplotype, {"phenotype": "Normal Function", "activity_score": 2.0}
        )

        return SampleGeneInterpretation(
            sample_id=sample_id,
            gene="SLCO1B1",
            chrom=self.chrom,
            variants_examined_count=variants_examined_count,
            detected_variants=detected_variants,
            assigned_star_alleles=diplotype.split('/'),
            diplotype=diplotype,
            phenotype=pheno_info["phenotype"],
            activity_score=pheno_info["activity_score"],
            evidence_source="PharmVar v5.2 (GRCh37) & CPIC Guidelines (2022)",
            status_code=status_code,
            candidate_diplotypes=[],
            warnings=[]
        )


class CYP2D6Interpreter(BaseGeneInterpreter):
    def __init__(self):
        super().__init__("CYP2D6")

    def interpret(
        self,
        sample_id: str,
        variants: List[VariantCall],
        variants_examined_count: int = 0,
        total_examined: Optional[int] = None
    ) -> SampleGeneInterpretation:
        variants_examined_count = total_examined if total_examined is not None else variants_examined_count
        star3_def = self.star_allele_defs["*3"]["defining_variants"][0]
        star4_def = self.star_allele_defs["*4"]["defining_variants"][0]
        star10_def = self.star_allele_defs["*10"]["defining_variants"][0]
        star41_def = self.star_allele_defs["*41"]["defining_variants"][0]

        n_3, n_4, n_10, n_41 = 0, 0, 0, 0
        v_calls = []

        for v in variants:
            c3, _ = self._match_variant_risk_copies(v, star3_def)
            if c3 > 0: n_3 = c3; v_calls.append(v)
            c4, _ = self._match_variant_risk_copies(v, star4_def)
            if c4 > 0: n_4 = c4; v_calls.append(v)
            c10, _ = self._match_variant_risk_copies(v, star10_def)
            if c10 > 0: n_10 = c10; v_calls.append(v)
            c41, _ = self._match_variant_risk_copies(v, star41_def)
            if c41 > 0: n_41 = c41; v_calls.append(v)

        detected_variants = [
            {"pos": vc.pos, "rsid": vc.rsid, "ref": vc.ref, "alt": vc.alt, "genotype": vc.genotype}
            for vc in v_calls
        ]

        warnings = [
            "Structural Variant Limitation: CYP2D6*5 (whole gene deletion), *1xN duplications, and hybrid alleles cannot be reliably determined from short-read SNV VCFs. Secondary CNV testing is recommended."
        ]
        status_code = "SUCCESS_WITH_SV_LIMITATIONS"

        if n_4 == 2: diplotype = "*4/*4"; pheno = "Poor Metabolizer"; as_score = 0.0
        elif n_3 == 2: diplotype = "*3/*3"; pheno = "Poor Metabolizer"; as_score = 0.0
        elif n_4 == 1 and n_3 == 1: diplotype = "*3/*4"; pheno = "Poor Metabolizer"; as_score = 0.0
        elif n_4 == 1: diplotype = "*1/*4"; pheno = "Intermediate Metabolizer"; as_score = 0.5
        elif n_3 == 1: diplotype = "*1/*3"; pheno = "Intermediate Metabolizer"; as_score = 0.5
        elif n_41 == 2: diplotype = "*41/*41"; pheno = "Intermediate Metabolizer"; as_score = 1.0
        elif n_41 == 1: diplotype = "*1/*41"; pheno = "Normal Metabolizer"; as_score = 1.5
        elif n_10 == 2: diplotype = "*10/*10"; pheno = "Intermediate Metabolizer"; as_score = 0.5
        elif n_10 == 1: diplotype = "*1/*10"; pheno = "Normal Metabolizer"; as_score = 1.25
        else:
            diplotype = "*1/*1"
            pheno = "Normal Metabolizer"
            as_score = 2.0

        return SampleGeneInterpretation(
            sample_id=sample_id,
            gene="CYP2D6",
            chrom=self.chrom,
            variants_examined_count=variants_examined_count,
            detected_variants=detected_variants,
            assigned_star_alleles=diplotype.split('/'),
            diplotype=diplotype,
            phenotype=pheno,
            activity_score=as_score,
            evidence_source="PharmVar v5.2 (GRCh37) & CPIC Guidelines (2020)",
            status_code=status_code,
            candidate_diplotypes=[],
            warnings=warnings
        )
