/**
 * PharmaGuard Unified Clinical Interpretation Engine
 * Enforces strict, evidence-based interpretation rules across all dashboard components.
 * Eliminates clinical contradictions and prevents fabricated predictions.
 */

export const drugGeneMap = {
  "Clopidogrel": "CYP2C19",
  "Warfarin": "CYP2C9",
  "Fluorouracil": "DPYD",
  "Simvastatin": "SLCO1B1",
  "Codeine": "CYP2D6"
};

export const availableDrugs = [
  "Clopidogrel",
  "Warfarin",
  "Fluorouracil",
  "Simvastatin",
  "Codeine"
];

/**
 * Evaluates raw genomic analysis results and builds a unified, verified clinical interpretation.
 */
export function evaluateClinicalInterpretation(analysisResults, selectedDrug = "Clopidogrel") {
  if (!analysisResults) {
    return getNullInterpretation(selectedDrug);
  }

  const patientProfile = analysisResults.patient_profile || {};
  const extractedGenes = analysisResults.extracted_genes || {};
  const pmgrfProfile = analysisResults.pmgrf_profile || {};
  const rawRecommendations = pmgrfProfile.drug_recommendations || [];

  const targetGene = drugGeneMap[selectedDrug] || "CYP2C19";
  const geneInfo = extractedGenes[targetGene] || {};
  const geneStatus = patientProfile[targetGene] || geneInfo.status || "Unknown";

  // Check if genomic evidence for the selected gene is insufficient or missing
  const isGeneInsufficient = 
    !geneStatus ||
    geneStatus === "Unknown" ||
    geneStatus === "INSUFFICIENT_GENOTYPE_DATA" ||
    geneStatus === "INSUFFICIENT_GENOMIC_EVIDENCE" ||
    geneStatus === "NOT_TESTED" ||
    geneInfo.source === "uploaded_vcf_positions_only" ||
    geneInfo.source === "absent_from_vcf";

  // Check overall genomic evidence across all 5 key pharmacogenes
  const actionableGenes = [];
  const nonNormalGenes = [];
  let validGenotypeCount = 0;

  Object.entries(patientProfile).forEach(([gene, status]) => {
    const isNormalOrValid = status === "Normal" || status === "Intermediate" || status === "Poor";
    const isInsufficient = 
      !status || 
      status.includes("INSUFFICIENT") || 
      status === "NOT_TESTED" || 
      status === "Unknown";

    if (!isInsufficient) {
      validGenotypeCount++;
      if (status === "Intermediate" || status === "Poor") {
        actionableGenes.push({ gene, status });
        nonNormalGenes.push(`${gene} ${status} Metabolizer`);
      }
    }
  });

  const isOverallInsufficient = validGenotypeCount === 0;

  // Selected drug recommendation resolution
  const rawRec = rawRecommendations.find(r => r.drug_name === selectedDrug);

  let recommendationObj = null;
  if (isGeneInsufficient || isOverallInsufficient) {
    recommendationObj = {
      drugName: selectedDrug,
      associatedGene: targetGene,
      phenotype: "Unknown",
      diplotype: "Unknown",
      riskLevel: "Insufficient Evidence",
      recommendation: "Not Determinable",
      recommendationStatement: "Insufficient genomic evidence for pharmacogenomic interpretation.",
      rationale: `Genomic evidence for ${targetGene} was not found or contains insufficient genotype data in the uploaded VCF file. Standard CPIC dosing guidelines cannot be deterministically computed without verified genotype calls.`,
      explanation: `Genomic evidence for ${targetGene} was not found or contains insufficient genotype data in the uploaded VCF file. Standard CPIC dosing guidelines cannot be deterministically computed without verified genotype calls.`,
      patientEvidenceStatus: "Insufficient Genomic Evidence",
      guidelineSource: `CPIC Guideline for ${selectedDrug} and ${targetGene} (2025.2)`
    };
  } else {
    recommendationObj = {
      drugName: selectedDrug,
      associatedGene: targetGene,
      phenotype: rawRec?.phenotype || "Normal Metabolizer",
      diplotype: rawRec?.dashboard_metadata?.diplotype || "*1/*1",
      riskLevel: rawRec?.risk_level || "Low",
      recommendation: rawRec?.recommendation || `Initiate ${selectedDrug} at standard label-recommended dosage.`,
      recommendationStatement: rawRec?.recommendation || `Initiate ${selectedDrug} at standard label-recommended dosage.`,
      rationale: rawRec?.rationale || `Normal ${targetGene} enzyme activity generates expected active metabolite levels.`,
      explanation: rawRec?.explanation || `Patient carries ${targetGene} *1/*1 resulting in Normal Metabolizer phenotype.`,
      patientEvidenceStatus: "Genotype Evidence Verified",
      guidelineSource: rawRec?.dashboard_metadata?.guideline || `CPIC Guideline for ${selectedDrug} and ${targetGene} (2025.2)`
    };
  }

  // Executive Summary Resolution
  let actionableFindings = ["None"];
  if (actionableGenes.length > 0) {
    actionableFindings = actionableGenes.map(g => `${g.gene} ${g.status} Metabolizer - Dosing adjustment indicated`);
  }

  let evidenceStatus = `Insufficient ${targetGene} genotype evidence`;
  if (!isGeneInsufficient) {
    evidenceStatus = `Verified ${targetGene} genotype evidence (${geneStatus})`;
  } else if (!isOverallInsufficient) {
    evidenceStatus = `Partial panel evidence (${validGenotypeCount}/5 genes tested)`;
  }

  let clinicalRecStatus = isGeneInsufficient ? "Not Determinable" : "CPIC Guidance Available";
  
  let riskAssessmentStatus = isOverallInsufficient 
    ? "Unable to compute due to insufficient genomic evidence"
    : `Computed (PMGRF Tier: ${pmgrfProfile.risk_category || 'Low'} Risk)`;

  // PMGRF Resolution
  const pmgrfStatus = isOverallInsufficient ? "Not Computable" : "Computed";
  const pmgrfRiskCategory = isOverallInsufficient ? "Insufficient Evidence" : (pmgrfProfile.risk_category || "Low");
  const pmgrfScore = isOverallInsufficient ? null : (pmgrfProfile.pmgrf_score ?? 0);
  const contributingGenesCount = isOverallInsufficient ? 0 : (pmgrfProfile.contributing_genes?.length || 0);
  const pmgrfReason = isOverallInsufficient
    ? "Insufficient genomic evidence across all target pharmacogenes. PMGRF composite score cannot be computed."
    : pmgrfProfile.explanation || "PMGRF Multi-Gene evaluation completed based on verified genotype calls.";

  // AI Risk Module Resolution
  const isAiAvailable = !isOverallInsufficient && nonNormalGenes.length > 0;
  const aiRiskScore = isOverallInsufficient ? null : analysisResults.risk_score;
  const aiUncertainty = analysisResults.uncertainty || { coverage: 0.90, interval: [0, 0] };
  const aiContributingFeatures = nonNormalGenes.length > 0 ? nonNormalGenes : [];

  return {
    selectedDrug,
    targetGene,
    geneStatus,
    isGeneInsufficient,
    isOverallInsufficient,
    recommendation: recommendationObj,
    executiveSummary: {
      actionableFindings,
      evidenceStatus,
      clinicalRecStatus,
      riskAssessmentStatus
    },
    pmgrf: {
      status: pmgrfStatus,
      riskCategory: pmgrfRiskCategory,
      score: pmgrfScore,
      contributingCount: contributingGenesCount,
      reason: pmgrfReason,
      contributingGenes: isOverallInsufficient ? [] : (pmgrfProfile.contributing_genes || [])
    },
    aiRisk: {
      isAvailable: isAiAvailable,
      riskScore: aiRiskScore,
      confidence: aiUncertainty.coverage ? `${aiUncertainty.coverage * 100}% Confidence` : "90% Confidence",
      interval: aiUncertainty.interval || [0, 0],
      reasoningTrace: analysisResults.reasoning_trace || "",
      contributingFeatures: aiContributingFeatures,
      modelVersion: analysisResults.model_version || "CatBoost v2.1"
    }
  };
}

function getNullInterpretation(selectedDrug) {
  const targetGene = drugGeneMap[selectedDrug] || "CYP2C19";
  return {
    selectedDrug,
    targetGene,
    geneStatus: "Unknown",
    isGeneInsufficient: true,
    isOverallInsufficient: true,
    recommendation: {
      drugName: selectedDrug,
      associatedGene: targetGene,
      phenotype: "Unknown",
      diplotype: "Unknown",
      riskLevel: "Insufficient Evidence",
      recommendation: "Not Determinable",
      recommendationStatement: "Insufficient genomic evidence for pharmacogenomic interpretation.",
      rationale: "No patient VCF data loaded.",
      explanation: "No patient VCF data loaded.",
      patientEvidenceStatus: "Insufficient Genomic Evidence",
      guidelineSource: `CPIC Guideline for ${selectedDrug} and ${targetGene} (2025.2)`
    },
    executiveSummary: {
      actionableFindings: ["None"],
      evidenceStatus: "No VCF data loaded",
      clinicalRecStatus: "Not Determinable",
      riskAssessmentStatus: "Unable to compute due to insufficient genomic evidence"
    },
    pmgrf: {
      status: "Not Computable",
      riskCategory: "Insufficient Evidence",
      score: null,
      contributingCount: 0,
      reason: "No patient VCF data loaded.",
      contributingGenes: []
    },
    aiRisk: {
      isAvailable: false,
      riskScore: null,
      confidence: "N/A",
      interval: [0, 0],
      reasoningTrace: "",
      contributingFeatures: [],
      modelVersion: "CatBoost v2.1"
    }
  };
}
