"""
Authoritative PharmVar and CPIC Reference Data (GRCh37 / hg19).
Contains allele definitions, core defining variants (with explicit risk_allele_vcf and wildtype_allele_vcf),
activity scores, and diplotype-to-phenotype translation tables.
"""

from typing import Dict, List, Any


# ==============================================================================
# PHARMVAR GRCh37 ALLELE DEFINITIONS WITH EXPLICIT RISK ALLELE ORIENTATIONS
# ==============================================================================

PHARMVAR_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "CYP2C19": {
        "gene": "CYP2C19",
        "chrom": "10",
        "reference_allele": "*1",
        "star_alleles": {
            "*1": {
                "function_status": "Normal Function",
                "activity_score": 1.0,
                "defining_variants": []
            },
            "*2": {
                "function_status": "No Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "10",
                        "pos_grch37": [96521422, 94781859],
                        "ref": "A",
                        "alt": "G",
                        "rsid": "rs4244285",
                        "risk_allele_vcf": "A",        # Explicit risk allele in VCF (REF in GRCh37)
                        "wildtype_allele_vcf": "G",    # Wildtype allele in VCF (ALT in GRCh37)
                        "impact": "splice_site_defect"
                    }
                ]
            },
            "*3": {
                "function_status": "No Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "10",
                        "pos_grch37": [96522556, 94781944],
                        "ref": "G",
                        "alt": "A",
                        "rsid": "rs4986893",
                        "risk_allele_vcf": "A",
                        "wildtype_allele_vcf": "G",
                        "impact": "stop_gained"
                    }
                ]
            },
            "*17": {
                "function_status": "Increased Function",
                "activity_score": 1.0,
                "defining_variants": [
                    {
                        "chrom": "10",
                        "pos_grch37": [96501538, 94761900],
                        "ref": "C",
                        "alt": "T",
                        "rsid": "rs12248560",
                        "risk_allele_vcf": "T",
                        "wildtype_allele_vcf": "C",
                        "impact": "promoter_hyper_expression"
                    }
                ]
            }
        }
    },
    "CYP2C9": {
        "gene": "CYP2C9",
        "chrom": "10",
        "reference_allele": "*1",
        "star_alleles": {
            "*1": {
                "function_status": "Normal Function",
                "activity_score": 1.0,
                "defining_variants": []
            },
            "*2": {
                "function_status": "Decreased Function",
                "activity_score": 0.5,
                "defining_variants": [
                    {
                        "chrom": "10",
                        "pos_grch37": [96699917, 94938683],
                        "ref": "C",
                        "alt": "T",
                        "rsid": "rs1799853",
                        "risk_allele_vcf": "T",
                        "wildtype_allele_vcf": "C",
                        "impact": "missense_R144C"
                    }
                ]
            },
            "*3": {
                "function_status": "Decreased Function",
                "activity_score": 0.5,
                "defining_variants": [
                    {
                        "chrom": "10",
                        "pos_grch37": [96702047, 94981296],
                        "ref": "C",
                        "alt": "T",
                        "rsid": "rs1057910",
                        "risk_allele_vcf": "T",
                        "wildtype_allele_vcf": "C",
                        "impact": "missense_I359L"
                    }
                ]
            }
        }
    },
    "DPYD": {
        "gene": "DPYD",
        "chrom": "1",
        "reference_allele": "*1",
        "star_alleles": {
            "*1": {
                "function_status": "Normal Function",
                "activity_score": 1.0,
                "defining_variants": []
            },
            "*2A": {
                "function_status": "No Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "1",
                        "pos_grch37": [97547947, 97915614],
                        "ref": "T",
                        "alt": "A",
                        "rsid": "rs3918290",
                        "risk_allele_vcf": "A",
                        "wildtype_allele_vcf": "T",
                        "impact": "c.1905+1G>A_splice_site"
                    }
                ]
            },
            "*13": {
                "function_status": "No Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "1",
                        "pos_grch37": [97450058, 97914047],
                        "ref": "T",
                        "alt": "G",
                        "rsid": "rs55886062",
                        "risk_allele_vcf": "G",
                        "wildtype_allele_vcf": "T",
                        "impact": "c.1679T>G_missense"
                    }
                ]
            },
            "c.2846A>T": {
                "function_status": "Decreased Function",
                "activity_score": 0.5,
                "defining_variants": [
                    {
                        "chrom": "1",
                        "pos_grch37": [97573863, 97980816],
                        "ref": "A",
                        "alt": "T",
                        "rsid": "rs67376798",
                        "risk_allele_vcf": "T",
                        "wildtype_allele_vcf": "A",
                        "impact": "c.2846A>T_missense"
                    }
                ]
            },
            "c.1129-5923C>G": {
                "function_status": "Decreased Function",
                "activity_score": 0.5,
                "defining_variants": [
                    {
                        "chrom": "1",
                        "pos_grch37": [98348885, 97573863],
                        "ref": "G",
                        "alt": "A",
                        "rsid": "rs75017182",
                        "risk_allele_vcf": "G",        # HapB3 risk allele in VCF (REF in GRCh37 assembly!)
                        "wildtype_allele_vcf": "A",    # Wildtype allele in VCF (ALT in GRCh37 assembly!)
                        "impact": "HapB3_intronic_splice"
                    }
                ]
            }
        }
    },
    "SLCO1B1": {
        "gene": "SLCO1B1",
        "chrom": "12",
        "reference_allele": "*1A",
        "star_alleles": {
            "*1A": {
                "function_status": "Normal Function",
                "activity_score": 1.0,
                "defining_variants": []
            },
            "*1B": {
                "function_status": "Normal Function",
                "activity_score": 1.0,
                "defining_variants": [
                    {
                        "chrom": "12",
                        "pos_grch37": [21284003, 21327153],
                        "ref": "A",
                        "alt": "G",
                        "rsid": "rs2306283",
                        "risk_allele_vcf": "G",
                        "wildtype_allele_vcf": "A",
                        "impact": "c.388A>G_missense"
                    }
                ]
            },
            "*5": {
                "function_status": "Decreased Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "12",
                        "pos_grch37": [21331549, 21331549],
                        "ref": "T",
                        "alt": "C",
                        "rsid": "rs4149056",
                        "risk_allele_vcf": "C",
                        "wildtype_allele_vcf": "T",
                        "impact": "c.521T>C_missense"
                    }
                ]
            }
        }
    },
    "CYP2D6": {
        "gene": "CYP2D6",
        "chrom": "22",
        "reference_allele": "*1",
        "star_alleles": {
            "*1": {
                "function_status": "Normal Function",
                "activity_score": 1.0,
                "defining_variants": []
            },
            "*3": {
                "function_status": "No Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "22",
                        "pos_grch37": [42523528, 42523528],
                        "ref": "AGT",
                        "alt": "A",
                        "rsid": "rs35742686",
                        "risk_allele_vcf": "A",
                        "wildtype_allele_vcf": "AGT",
                        "impact": "2549delA_frameshift"
                    }
                ]
            },
            "*4": {
                "function_status": "No Function",
                "activity_score": 0.0,
                "defining_variants": [
                    {
                        "chrom": "22",
                        "pos_grch37": [42524244, 42524244],
                        "ref": "G",
                        "alt": "A",
                        "rsid": "rs3892097",
                        "risk_allele_vcf": "A",
                        "wildtype_allele_vcf": "G",
                        "impact": "1846G>A_splice_site"
                    }
                ]
            },
            "*10": {
                "function_status": "Decreased Function",
                "activity_score": 0.25,
                "defining_variants": [
                    {
                        "chrom": "22",
                        "pos_grch37": [42522612, 42522612],
                        "ref": "C",
                        "alt": "T",
                        "rsid": "rs1065852",
                        "risk_allele_vcf": "T",
                        "wildtype_allele_vcf": "C",
                        "impact": "100C>T_missense"
                    }
                ]
            },
            "*41": {
                "function_status": "Decreased Function",
                "activity_score": 0.5,
                "defining_variants": [
                    {
                        "chrom": "22",
                        "pos_grch37": [42526694, 42526694],
                        "ref": "G",
                        "alt": "A",
                        "rsid": "rs28371725",
                        "risk_allele_vcf": "A",
                        "wildtype_allele_vcf": "G",
                        "impact": "2988G>A_splice"
                    }
                ]
            }
        }
    }
}


# ==============================================================================
# CPIC DIPLOTYPE TO PHENOTYPE TRANSLATION TABLES
# ==============================================================================

CPIC_PHENOTYPE_RULES = {
    "CYP2C19": {
        "guideline": "CPIC Guideline for CYP2C19 (2022 Update)",
        "translation": {
            "*17/*17": {"phenotype": "Ultrarapid Metabolizer", "activity_score": 2.0},
            "*1/*17": {"phenotype": "Rapid Metabolizer", "activity_score": 1.5},
            "*1/*1": {"phenotype": "Normal Metabolizer", "activity_score": 1.0},
            "*1/*2": {"phenotype": "Intermediate Metabolizer", "activity_score": 0.5},
            "*1/*3": {"phenotype": "Intermediate Metabolizer", "activity_score": 0.5},
            "*2/*17": {"phenotype": "Intermediate Metabolizer", "activity_score": 0.5},
            "*3/*17": {"phenotype": "Intermediate Metabolizer", "activity_score": 0.5},
            "*2/*2": {"phenotype": "Poor Metabolizer", "activity_score": 0.0},
            "*2/*3": {"phenotype": "Poor Metabolizer", "activity_score": 0.0},
            "*3/*3": {"phenotype": "Poor Metabolizer", "activity_score": 0.0},
        }
    },
    "CYP2C9": {
        "guideline": "CPIC Guideline for CYP2C9 (2020 Update)",
        "translation": {
            "*1/*1": {"phenotype": "Normal Metabolizer", "activity_score": 2.0},
            "*1/*2": {"phenotype": "Normal Metabolizer", "activity_score": 1.5},
            "*1/*3": {"phenotype": "Intermediate Metabolizer", "activity_score": 1.0},
            "*2/*2": {"phenotype": "Intermediate Metabolizer", "activity_score": 1.0},
            "*2/*3": {"phenotype": "Intermediate Metabolizer", "activity_score": 0.5},
            "*3/*3": {"phenotype": "Poor Metabolizer", "activity_score": 0.0},
        }
    },
    "DPYD": {
        "guideline": "CPIC Guideline for DPYD (2017/2022 Update)",
        "translation": {}
    },
    "SLCO1B1": {
        "guideline": "CPIC Guideline for SLCO1B1 (2022 Update)",
        "translation": {
            "*1A/*1A": {"phenotype": "Normal Function", "activity_score": 2.0},
            "*1A/*1B": {"phenotype": "Normal Function", "activity_score": 2.0},
            "*1B/*1B": {"phenotype": "Normal Function", "activity_score": 2.0},
            "*1A/*5": {"phenotype": "Decreased Function", "activity_score": 1.0},
            "*1B/*5": {"phenotype": "Decreased Function", "activity_score": 1.0},
            "*5/*5": {"phenotype": "Poor Function", "activity_score": 0.0},
        }
    },
    "CYP2D6": {
        "guideline": "CPIC Guideline for CYP2D6 (2020 Update)",
        "translation": {}
    }
}
