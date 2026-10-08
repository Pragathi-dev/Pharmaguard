"""
PharmaGuard Multi-Gene Risk Framework (PMGRF) - Research Layer.
Aggregates individual gene-level PGx phenotype interpretations across key pharmacogenes
(CYP2C19, CYP2C9, DPYD, SLCO1B1, CYP2D6) into a Composite Pharmacogenomic Risk Score,
determines risk category (Low, Moderate, High), and provides full explainability.
Integrates with CPIC Drug Recommendation Engine for comprehensive patient risk profiling.
"""

from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass, field
from backend.pgx.data_model import SampleGeneInterpretation


# ==============================================================================
# PHENOTYPE SEVERITY SCORING MAPPINGS
# ==============================================================================

PHENOTYPE_SEVERITY_SCORES: Dict[str, Dict[str, int]] = {
    "CYP2C19": {
        "Normal Metabolizer": 0,
        "Normal": 0,
        "Intermediate Metabolizer": 1,
        "Intermediate": 1,
        "Poor Metabolizer": 2,
        "Poor": 2,
        "Rapid Metabolizer": 1,
        "Rapid": 1,
        "Ultrarapid Metabolizer": 2,
        "Ultrarapid": 2,
    },
    "CYP2C9": {
        "Normal Metabolizer": 0,
        "Normal": 0,
        "Intermediate Metabolizer": 1,
        "Intermediate": 1,
        "Poor Metabolizer": 2,
        "Poor": 2,
    },
    "DPYD": {
        "Normal Metabolizer": 0,
        "Normal": 0,
        "Intermediate Metabolizer": 2,
        "Intermediate": 2,
        "Poor Metabolizer": 3,
        "Poor": 3,
    },
    "SLCO1B1": {
        "Normal Function": 0,
        "Normal": 0,
        "Normal Metabolizer": 0,
        "Decreased Function": 2,
        "Decreased": 2,
        "Poor Function": 3,
        "Poor": 3,
    },
    "CYP2D6": {
        "Normal Metabolizer": 0,
        "Normal": 0,
        "Intermediate Metabolizer": 1,
        "Intermediate": 1,
        "Poor Metabolizer": 2,
        "Poor": 2,
        "Ultrarapid Metabolizer": 2,
        "Ultrarapid": 2,
    }
}


@dataclass
class MultiGeneRiskResult:
    """Composite Multi-Gene Risk Assessment Result."""
    sample_id: str
    total_score: int
    risk_category: str  # "Low", "Moderate", "High"
    contributing_genes: List[Dict[str, Any]] = field(default_factory=list)
    evaluated_genes: List[Dict[str, Any]] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "total_score": self.total_score,
            "risk_category": self.risk_category,
            "contributing_genes": self.contributing_genes,
            "evaluated_genes": self.evaluated_genes,
            "explanation": self.explanation
        }


@dataclass
class ComprehensivePatientProfile:
    """Unified Integrated PMGRF and CPIC Drug Recommendation Profile."""
    sample_id: str
    pmgrf_score: int
    risk_category: str
    contributing_genes: List[Dict[str, Any]] = field(default_factory=list)
    drug_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    evaluated_genes: List[Dict[str, Any]] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "pmgrf_score": self.pmgrf_score,
            "risk_category": self.risk_category,
            "contributing_genes": self.contributing_genes,
            "drug_recommendations": self.drug_recommendations
        }


class MultiGeneRiskEvaluator:
    """
    PharmaGuard Multi-Gene Risk Framework (PMGRF) Evaluator.
    Calculates composite risk scores and generates explainable summaries.
    """

    @staticmethod
    def get_phenotype_severity_score(gene: str, phenotype: str) -> int:
        """
        Looks up the severity score for a gene phenotype.
        Defaults to 0 if phenotype is normal or unknown.
        """
        gene_mapping = PHENOTYPE_SEVERITY_SCORES.get(gene, {})
        if phenotype in gene_mapping:
            return gene_mapping[phenotype]
        
        # Case-insensitive / substring fallback matching
        pheno_lower = phenotype.lower().strip()
        for k, v in gene_mapping.items():
            if k.lower() == pheno_lower:
                return v
        
        if "poor" in pheno_lower:
            return 3 if gene in ["DPYD", "SLCO1B1"] else 2
        elif "decreased" in pheno_lower:
            return 2
        elif "intermediate" in pheno_lower:
            return 2 if gene == "DPYD" else 1
        elif "ultrarapid" in pheno_lower:
            return 2
        elif "rapid" in pheno_lower:
            return 1
        
        return 0

    @classmethod
    def evaluate_sample_risk(
        cls,
        interpretations: Union[
            Dict[str, Union[SampleGeneInterpretation, Dict[str, Any]]],
            List[Union[SampleGeneInterpretation, Dict[str, Any]]]
        ],
        sample_id: Optional[str] = None
    ) -> MultiGeneRiskResult:
        """
        Aggregates gene interpretations and computes composite risk score.
        Accepts dict mapping gene_name -> interpretation OR list of interpretations.
        """
        interp_list: List[Dict[str, Any]] = []

        if isinstance(interpretations, dict):
            for k, val in interpretations.items():
                if isinstance(val, SampleGeneInterpretation):
                    interp_list.append(val.to_dict())
                elif isinstance(val, dict):
                    interp_list.append(val)
        elif isinstance(interpretations, list):
            for item in interpretations:
                if isinstance(item, SampleGeneInterpretation):
                    interp_list.append(item.to_dict())
                elif isinstance(item, dict):
                    interp_list.append(item)

        extracted_sample_id = sample_id or "UNKNOWN_SAMPLE"
        evaluated_genes: List[Dict[str, Any]] = []
        contributing_genes: List[Dict[str, Any]] = []
        total_score = 0

        for item in interp_list:
            gene = item.get("gene", "UNKNOWN")
            if extracted_sample_id == "UNKNOWN_SAMPLE" and item.get("sample_id"):
                extracted_sample_id = item.get("sample_id")

            phenotype = item.get("phenotype", "Normal Metabolizer")
            diplotype = item.get("diplotype", "*1/*1")
            act_score = item.get("activity_score")
            status_code = item.get("status_code", "CONFIDENTLY_RESOLVED")

            severity_score = cls.get_phenotype_severity_score(gene, phenotype)
            total_score += severity_score

            gene_summary = {
                "gene": gene,
                "phenotype": phenotype,
                "diplotype": diplotype,
                "activity_score": act_score,
                "severity_score": severity_score,
                "status_code": status_code
            }

            evaluated_genes.append(gene_summary)
            if severity_score > 0:
                contributing_genes.append(gene_summary)

        # Categorize risk score: 0-2 Low, 3-5 Moderate, 6+ High
        if total_score <= 2:
            risk_category = "Low"
        elif total_score <= 5:
            risk_category = "Moderate"
        else:
            risk_category = "High"

        explanation = cls._generate_explanation(
            extracted_sample_id, total_score, risk_category, evaluated_genes, contributing_genes
        )

        return MultiGeneRiskResult(
            sample_id=extracted_sample_id,
            total_score=total_score,
            risk_category=risk_category,
            contributing_genes=contributing_genes,
            evaluated_genes=evaluated_genes,
            explanation=explanation
        )

    @classmethod
    def evaluate_comprehensive_patient_profile(
        cls,
        interpretations: Union[
            Dict[str, Union[SampleGeneInterpretation, Dict[str, Any]]],
            List[Union[SampleGeneInterpretation, Dict[str, Any]]]
        ],
        sample_id: Optional[str] = None
    ) -> ComprehensivePatientProfile:
        """
        Integrates PMGRF risk scoring with CPIC Drug Recommendation Engine.
        Returns a ComprehensivePatientProfile with exact requested output schema.
        """
        from backend.pgx.drug_recommendation_engine import DrugRecommendationEngine

        pmgrf_res = cls.evaluate_sample_risk(interpretations, sample_id)
        drug_recs = DrugRecommendationEngine.get_all_drug_recommendations(interpretations)
        drug_recs_dict = [r.to_dict() for r in drug_recs]

        return ComprehensivePatientProfile(
            sample_id=pmgrf_res.sample_id,
            pmgrf_score=pmgrf_res.total_score,
            risk_category=pmgrf_res.risk_category,
            contributing_genes=pmgrf_res.contributing_genes,
            drug_recommendations=drug_recs_dict,
            evaluated_genes=pmgrf_res.evaluated_genes,
            explanation=pmgrf_res.explanation
        )

    @staticmethod
    def _generate_explanation(
        sample_id: str,
        total_score: int,
        risk_category: str,
        evaluated_genes: List[Dict[str, Any]],
        contributing_genes: List[Dict[str, Any]]
    ) -> str:
        lines = []
        lines.append(f"### PharmaGuard Multi-Gene Risk Framework (PMGRF) Assessment")
        lines.append(f"**Sample ID**: `{sample_id}`  ")
        lines.append(f"**Composite PGx Risk Score**: **{total_score}**  ")
        lines.append(f"**Overall Risk Category**: **{risk_category.upper()}** (Score Range: 0-2 Low, 3-5 Moderate, 6+ High)  \n")

        if not contributing_genes:
            lines.append("#### Assessment Rationale")
            lines.append("All evaluated pharmacogenes (`" + ", ".join([g["gene"] for g in evaluated_genes]) + "`) exhibit **Normal / Baseline** functional phenotypes. No elevated pharmacogenomic severity risks were identified.")
        else:
            lines.append(f"#### Contributing High-Risk Pharmacogenes ({len(contributing_genes)} identified):")
            for g in contributing_genes:
                lines.append(
                    f"- **{g['gene']}**: Phenotype = `{g['phenotype']}` (Diplotype: `{g['diplotype']}`) "
                    f"-> **Severity Score: +{g['severity_score']}**"
                )
            lines.append("\n#### Assessment Rationale")
            lines.append(
                f"The composite score of **{total_score}** places this patient in the **{risk_category} Risk** tier due to cumulative non-normal functional variants across "
                + ", ".join([f"**{g['gene']}** ({g['phenotype']})" for g in contributing_genes]) + "."
            )

        return "\n".join(lines)
