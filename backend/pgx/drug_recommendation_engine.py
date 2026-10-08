"""
CPIC-Guideline-Based Drug Recommendation Engine with Explainability Layer.
Consumes gene interpretation outputs for CYP2C19, CYP2C9, DPYD, SLCO1B1, and CYP2D6
and generates authentic CPIC clinical drug recommendations, human-readable narrative explanations,
and structured dashboard metadata for Clopidogrel, Warfarin, Fluorouracil/5-FU, Simvastatin, and Codeine.
"""

from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass, field
from backend.pgx.data_model import SampleGeneInterpretation


@dataclass
class DrugRecommendation:
    """Clinical Pharmacogenomic Drug Recommendation Output with Explainability."""
    drug_name: str
    associated_gene: str
    phenotype: str
    risk_level: str  # "Low", "Moderate", "High"
    recommendation: str
    rationale: str
    explanation: str
    dashboard_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "drug_name": self.drug_name,
            "associated_gene": self.associated_gene,
            "phenotype": self.phenotype,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "rationale": self.rationale,
            "explanation": self.explanation,
            "dashboard_metadata": self.dashboard_metadata
        }


# ==============================================================================
# AUTHORITATIVE CPIC GUIDELINE DRUG MAPPINGS & EXPLAINABILITY TEMPLATES
# ==============================================================================

CPIC_DRUG_MAP: Dict[str, Dict[str, Any]] = {
    "Clopidogrel": {
        "gene": "CYP2C19",
        "guideline": "CPIC Guideline for Clopidogrel and CYP2C19 (2022 Update)",
        "rules": {
            "Ultrarapid Metabolizer": {
                "risk_level": "Low",
                "recommendation": "Initiate Clopidogrel at standard label-recommended dosage (75 mg once daily).",
                "rationale": "Increased CYP2C19 bioactivation yields adequate or superior active metabolite levels and effective antiplatelet response.",
                "mechanism": "Increased conversion of clopidogrel into its active metabolite provides expected or superior antiplatelet efficacy.",
                "action": "Standard clopidogrel therapy is recommended",
                "alternatives": []
            },
            "Rapid Metabolizer": {
                "risk_level": "Low",
                "recommendation": "Initiate Clopidogrel at standard label-recommended dosage (75 mg once daily).",
                "rationale": "Increased CYP2C19 bioactivation yields adequate active metabolite levels and effective antiplatelet response.",
                "mechanism": "Increased conversion of clopidogrel into its active metabolite provides expected antiplatelet efficacy.",
                "action": "Standard clopidogrel therapy is recommended",
                "alternatives": []
            },
            "Normal Metabolizer": {
                "risk_level": "Low",
                "recommendation": "Initiate Clopidogrel at standard label-recommended dosage (75 mg once daily).",
                "rationale": "Normal CYP2C19 enzyme activity generates expected active metabolite levels for antiplatelet efficacy.",
                "mechanism": "Normal bioactivation of clopidogrel generates adequate active metabolite exposure.",
                "action": "Standard clopidogrel therapy is recommended",
                "alternatives": []
            },
            "Intermediate Metabolizer": {
                "risk_level": "Moderate",
                "recommendation": "Avoid Clopidogrel. Select an alternative antiplatelet agent such as Prasugrel or Ticagrelor if not contraindicated.",
                "rationale": "Reduced CYP2C19 bioactivation leads to decreased active metabolite exposure and increased risk of major adverse cardiovascular events (MACE) and stent thrombosis.",
                "mechanism": "Reduced conversion of clopidogrel into its active metabolite may decrease therapeutic effectiveness.",
                "action": "Alternative antiplatelet therapy (e.g., Prasugrel or Ticagrelor) should be considered",
                "alternatives": ["Prasugrel", "Ticagrelor"]
            },
            "Poor Metabolizer": {
                "risk_level": "High",
                "recommendation": "Avoid Clopidogrel. Use an alternative antiplatelet agent such as Prasugrel or Ticagrelor unless contraindicated.",
                "rationale": "Markedly deficient CYP2C19 enzyme activity prevents conversion to active metabolite, resulting in clinical non-responsiveness and significantly elevated stent thrombosis risk.",
                "mechanism": "Absence of CYP2C19 bioactivation prevents conversion of clopidogrel into its active metabolite, leading to therapeutic failure and high stent thrombosis risk.",
                "action": "Alternative antiplatelet therapy (e.g., Prasugrel or Ticagrelor) must be prescribed",
                "alternatives": ["Prasugrel", "Ticagrelor"]
            }
        }
    },
    "Warfarin": {
        "gene": "CYP2C9",
        "guideline": "CPIC Guideline for Warfarin Dosing and CYP2C9/VKORC1/CYP4F2 (2020 Update)",
        "rules": {
            "Normal Metabolizer": {
                "risk_level": "Low",
                "recommendation": "Initiate Warfarin at standard starting dose (e.g., 5 mg daily) and adjust according to INR monitoring.",
                "rationale": "Standard S-warfarin metabolic clearance rate; routine clinical dosing algorithms apply.",
                "mechanism": "Standard S-warfarin clearance provides predictable anticoagulation response.",
                "action": "Standard starting dose and routine INR monitoring are recommended",
                "alternatives": []
            },
            "Intermediate Metabolizer": {
                "risk_level": "Moderate",
                "recommendation": "Reduce initial Warfarin starting dose by 25% to 50% or utilize CPIC pharmacogenomic dosing algorithms; monitor INR frequently.",
                "rationale": "Decreased S-warfarin clearance increases systemic exposure and elevates risk of over-anticoagulation and bleeding.",
                "mechanism": "Reduced S-warfarin clearance increases drug accumulation and risk of over-anticoagulation.",
                "action": "Initial dose reduction of 25-50% and frequent INR monitoring are recommended",
                "alternatives": ["DOACs (Apixaban, Rivaroxaban)"]
            },
            "Poor Metabolizer": {
                "risk_level": "High",
                "recommendation": "Significantly reduce Warfarin starting dose by 50% to 80% or consider an alternative anticoagulant (e.g., direct oral anticoagulant / DOAC) if clinically suitable.",
                "rationale": "Severely impaired S-warfarin clearance leads to drug accumulation, prolonged elevated INR, and severe risk of major bleeding complications.",
                "mechanism": "Severely impaired S-warfarin clearance causes major drug accumulation and high risk of bleeding.",
                "action": "Substantial dose reduction (50-80%) or alternative non-coumarin anticoagulant therapy should be selected",
                "alternatives": ["Apixaban", "Rivaroxaban", "Dabigatran"]
            }
        }
    },
    "Fluorouracil": {
        "gene": "DPYD",
        "guideline": "CPIC Guideline for Fluoropyrimidines and DPYD (2017/2022 Update)",
        "rules": {
            "Normal Metabolizer": {
                "risk_level": "Low",
                "recommendation": "Use standard label-recommended starting dose of Fluorouracil or Capecitabine.",
                "rationale": "Normal DPD enzyme activity provides full metabolic clearance of fluoropyrimidines.",
                "mechanism": "Normal DPD enzyme catabolism ensures expected drug elimination.",
                "action": "Standard fluoropyrimidine dosing is recommended",
                "alternatives": []
            },
            "Intermediate Metabolizer": {
                "risk_level": "Moderate",
                "recommendation": "Reduce Fluorouracil or Capecitabine starting dose by 25% to 50% based on activity score. Monitor closely for toxicities.",
                "rationale": "Reduced DPD enzyme clearance leads to increased systemic fluorouracil exposure and elevated risk of severe toxicities (neutropenia, severe diarrhea, mucositis).",
                "mechanism": "Decreased DPD clearance leads to increased systemic drug exposure and risk of severe adverse toxicity.",
                "action": "Starting dose reduction of 25-50% and close toxicity monitoring are recommended",
                "alternatives": ["Non-fluoropyrimidine chemotherapy"]
            },
            "Poor Metabolizer": {
                "risk_level": "High",
                "recommendation": "Avoid Fluorouracil and Capecitabine completely. Select an alternative non-fluoropyrimidine chemotherapy regimen.",
                "rationale": "Complete or near-complete DPD enzyme deficiency leads to severe drug accumulation, resulting in life-threatening or fatal fluoropyrimidine toxicity.",
                "mechanism": "Complete or severe DPD deficiency prevents fluoropyrimidine breakdown, leading to severe or fatal toxicity.",
                "action": "Fluorouracil and Capecitabine must be avoided completely",
                "alternatives": ["Non-fluoropyrimidine regimens (e.g. Irinotecan/Oxaliplatin-based)"]
            }
        }
    },
    "Simvastatin": {
        "gene": "SLCO1B1",
        "guideline": "CPIC Guideline for Statin Therapy and SLCO1B1/ABCG2/CYP2C9 (2022 Update)",
        "rules": {
            "Normal Function": {
                "risk_level": "Low",
                "recommendation": "Initiate desired starting dose of Simvastatin according to product label.",
                "rationale": "Normal OATP1B1 hepatic uptake transport ensures standard statin clearance without heightened myopathy risk.",
                "mechanism": "Normal OATP1B1 hepatic transporter uptake ensures routine statin clearance.",
                "action": "Standard simvastatin dosing is recommended",
                "alternatives": []
            },
            "Decreased Function": {
                "risk_level": "Moderate",
                "recommendation": "Limit Simvastatin dose to <=20 mg daily, or consider an alternative statin with lower OATP1B1 dependence (e.g., Rosuvastatin, Atorvastatin, Pravastatin).",
                "rationale": "Decreased OATP1B1 transport increases systemic plasma concentrations of simvastatin, elevating risk of statin-associated muscle symptoms (SAMS) and myopathy.",
                "mechanism": "Reduced OATP1B1 hepatic transport increases plasma statin exposure and myopathy risk.",
                "action": "Simvastatin dose should be limited to <=20 mg daily or an alternative statin selected",
                "alternatives": ["Rosuvastatin", "Atorvastatin", "Pravastatin"]
            },
            "Poor Function": {
                "risk_level": "High",
                "recommendation": "Avoid Simvastatin or limit dose to <=10 mg daily. Select an alternative statin (Rosuvastatin, Atorvastatin, Pravastatin) or non-statin lipid-lowering therapy.",
                "rationale": "Severely impaired hepatic transport leads to marked systemic statin accumulation, significantly increasing the risk of severe myopathy and rhabdomyolysis.",
                "mechanism": "Severely impaired hepatic transporter uptake causes statin accumulation and high rhabdomyolysis risk.",
                "action": "Simvastatin should be avoided or dose capped at <=10 mg daily with alternative statins strongly preferred",
                "alternatives": ["Rosuvastatin", "Atorvastatin", "Pravastatin"]
            }
        }
    },
    "Codeine": {
        "gene": "CYP2D6",
        "guideline": "CPIC Guideline for Codeine and CYP2D6 (2020 Update)",
        "rules": {
            "Ultrarapid Metabolizer": {
                "risk_level": "High",
                "recommendation": "Avoid Codeine due to risk of life-threatening toxicity. Select an alternative non-opioid or non-CYP2D6-dependent analgesic.",
                "rationale": "Rapid and extensive conversion of codeine to morphine results in toxic morphine plasma levels, carrying severe risk of respiratory depression.",
                "mechanism": "Rapid conversion of codeine to morphine produces toxic morphine plasma concentrations and severe respiratory depression risk.",
                "action": "Codeine must be avoided due to life-threatening toxicity risks",
                "alternatives": ["Non-opioids (Acetaminophen/NSAIDs)", "Morphine", "Non-CYP2D6 analgesics"]
            },
            "Normal Metabolizer": {
                "risk_level": "Low",
                "recommendation": "Initiate Codeine at standard label-recommended age- and weight-adjusted starting dose.",
                "rationale": "Normal CYP2D6 metabolic conversion generates therapeutic morphine levels for expected analgesic efficacy.",
                "mechanism": "Normal CYP2D6 bioactivation generates expected therapeutic morphine levels.",
                "action": "Standard codeine dosing is recommended",
                "alternatives": []
            },
            "Intermediate Metabolizer": {
                "risk_level": "Moderate",
                "recommendation": "Monitor for inadequate pain relief. If analgesia is insufficient, consider an alternative non-CYP2D6 opioid or non-opioid analgesic.",
                "rationale": "Reduced CYP2D6 bioactivation may yield subtherapeutic morphine concentrations, leading to reduced analgesic efficacy.",
                "mechanism": "Reduced CYP2D6 bioactivation may produce inadequate morphine levels and insufficient pain relief.",
                "action": "Monitoring for adequate efficacy or switching to an alternative analgesic is recommended",
                "alternatives": ["Morphine", "Non-opioids"]
            },
            "Poor Metabolizer": {
                "risk_level": "High",
                "recommendation": "Avoid Codeine due to lack of efficacy. Use an alternative analgesic not dependent on CYP2D6 bioactivation (e.g., Morphine, Non-opioids).",
                "rationale": "Absence of functional CYP2D6 enzyme prevents conversion of codeine to active morphine, resulting in complete lack of pain relief.",
                "mechanism": "Absence of CYP2D6 bioactivation prevents conversion to active morphine, causing complete lack of analgesic effect.",
                "action": "Codeine should be avoided due to complete therapeutic non-responsiveness",
                "alternatives": ["Morphine", "Non-opioids (Acetaminophen/NSAIDs)"]
            }
        }
    }
}

DRUG_ALIASES = {
    "5-fu": "Fluorouracil",
    "5-fluorouracil": "Fluorouracil",
    "capecitabine": "Fluorouracil",
    "fluorouracil / 5-fu": "Fluorouracil",
    "clopidogrel": "Clopidogrel",
    "warfarin": "Warfarin",
    "simvastatin": "Simvastatin",
    "codeine": "Codeine"
}


class DrugRecommendationEngine:
    """
    CPIC-Guideline-Based Clinical Drug Recommendation Engine with Explainability Layer.
    Translates gene interpretations into actionable prescribing guidance, human-readable
    explanations, and UI dashboard metadata.
    """

    @classmethod
    def get_recommendation_for_drug(
        cls,
        drug_name: str,
        gene_interpretation: Union[SampleGeneInterpretation, Dict[str, Any]]
    ) -> DrugRecommendation:
        """
        Generates CPIC drug recommendation with explanation and dashboard metadata.
        """
        canonical_drug = DRUG_ALIASES.get(drug_name.lower().strip(), drug_name.strip())
        if canonical_drug not in CPIC_DRUG_MAP:
            raise ValueError(f"Unsupported drug '{drug_name}'. Supported drugs: {list(CPIC_DRUG_MAP.keys())}")

        drug_info = CPIC_DRUG_MAP[canonical_drug]
        assoc_gene = drug_info["gene"]

        # Extract phenotype and diplotype strings
        if isinstance(gene_interpretation, SampleGeneInterpretation):
            phenotype = gene_interpretation.phenotype
            diplotype = gene_interpretation.diplotype
        elif isinstance(gene_interpretation, dict):
            phenotype = gene_interpretation.get("phenotype", "Normal Metabolizer")
            diplotype = gene_interpretation.get("diplotype", "*1/*1")
        else:
            phenotype = "Normal Metabolizer"
            diplotype = "*1/*1"

        rules = drug_info["rules"]
        rec_data = None

        if phenotype in rules:
            rec_data = rules[phenotype]
        else:
            ph_lower = phenotype.lower().strip()
            for k, v in rules.items():
                if k.lower() == ph_lower:
                    rec_data = v
                    break

            if not rec_data:
                if "poor" in ph_lower:
                    rec_data = rules.get("Poor Metabolizer") or rules.get("Poor Function")
                elif "intermediate" in ph_lower or "decreased" in ph_lower:
                    rec_data = rules.get("Intermediate Metabolizer") or rules.get("Decreased Function")
                elif "ultrarapid" in ph_lower:
                    rec_data = rules.get("Ultrarapid Metabolizer")
                elif "rapid" in ph_lower:
                    rec_data = rules.get("Rapid Metabolizer")
                elif "normal" in ph_lower:
                    rec_data = rules.get("Normal Metabolizer") or rules.get("Normal Function")

        if not rec_data:
            rec_data = {
                "risk_level": "Low",
                "recommendation": f"Initiate {canonical_drug} using standard clinical dosing guidelines.",
                "rationale": f"Phenotype '{phenotype}' for {assoc_gene} does not present elevated PGx clinical risk flags under CPIC guidelines.",
                "mechanism": f"Metabolic clearance for {canonical_drug} proceeds as expected.",
                "action": f"Standard {canonical_drug} therapy is recommended",
                "alternatives": []
            }

        # Determine a/an grammar for phenotype narrative
        a_an = "an" if phenotype[0].lower() in "aeiou" else "a"
        drug_label = canonical_drug.lower()

        # Construct human-readable narrative explanation matching requested pattern:
        # "Patient carries [Gene] [Diplotype] resulting in a/an [Phenotype] phenotype. [Biological Impact]. [Clinical Action] according to CPIC guidance."
        explanation = (
            f"Patient carries {assoc_gene} {diplotype} resulting in {a_an} {phenotype} phenotype. "
            f"{rec_data['mechanism']} {rec_data['action']} according to CPIC guidance."
        )

        dashboard_metadata = {
            "drug": canonical_drug,
            "gene": assoc_gene,
            "diplotype": diplotype,
            "phenotype": phenotype,
            "risk_badge": rec_data["risk_level"],
            "action_required": rec_data["risk_level"] in ["Moderate", "High"],
            "alternative_drugs_suggested": rec_data.get("alternatives", []),
            "guideline": drug_info.get("guideline", "CPIC Guideline")
        }

        return DrugRecommendation(
            drug_name=canonical_drug,
            associated_gene=assoc_gene,
            phenotype=phenotype,
            risk_level=rec_data["risk_level"],
            recommendation=rec_data["recommendation"],
            rationale=rec_data["rationale"],
            explanation=explanation,
            dashboard_metadata=dashboard_metadata
        )

    @classmethod
    def get_all_drug_recommendations(
        cls,
        interpretations: Union[
            Dict[str, Union[SampleGeneInterpretation, Dict[str, Any]]],
            List[Union[SampleGeneInterpretation, Dict[str, Any]]]
        ]
    ) -> List[DrugRecommendation]:
        """
        Generates CPIC drug recommendations with explainability for all 5 supported target drugs.
        """
        interp_by_gene: Dict[str, Any] = {}

        if isinstance(interpretations, dict):
            for k, val in interpretations.items():
                if isinstance(val, SampleGeneInterpretation):
                    interp_by_gene[val.gene] = val
                elif isinstance(val, dict):
                    gene_name = val.get("gene", k)
                    interp_by_gene[gene_name] = val
        elif isinstance(interpretations, list):
            for item in interpretations:
                if isinstance(item, SampleGeneInterpretation):
                    interp_by_gene[item.gene] = item
                elif isinstance(item, dict):
                    gene_name = item.get("gene", "UNKNOWN")
                    interp_by_gene[gene_name] = item

        recommendations: List[DrugRecommendation] = []

        for drug, drug_info in CPIC_DRUG_MAP.items():
            assoc_gene = drug_info["gene"]
            gene_interp = interp_by_gene.get(assoc_gene, {
                "gene": assoc_gene,
                "phenotype": "Normal Function" if assoc_gene == "SLCO1B1" else "Normal Metabolizer",
                "diplotype": "*1A/*1A" if assoc_gene == "SLCO1B1" else "*1/*1"
            })
            rec = cls.get_recommendation_for_drug(drug, gene_interp)
            recommendations.append(rec)

        return recommendations
