# knowledge_base.py

# This dictionary is your "Model". It maps exact DNA mutations to medical facts.
PHARMA_DB = {
    "TPMT": {
        "rs1800462": {
            "allele": "*2", 
            "phenotype": "Poor Metabolizer", 
            "risk_weight": 85.0,
            "warning": "High risk of severe myelosuppression with thiopurines (Azathioprine)."
        },
        "rs1142345": {
            "allele": "*3A", 
            "phenotype": "Poor Metabolizer", 
            "risk_weight": 85.0,
            "warning": "High risk of severe myelosuppression with thiopurines (Azathioprine)."
        }
    },
    "CYP2D6": {
        "rs3892097": {
            "allele": "*4", 
            "phenotype": "Poor Metabolizer", 
            "risk_weight": 70.0,
            "warning": "Reduced efficacy for tamoxifen; high toxicity risk for codeine."
        }
    },
    "CYP2C19": {
        "rs4244285": {
            "allele": "*2",
            "phenotype": "Poor Metabolizer",
            "risk_weight": 65.0,
            "warning": "Reduced efficacy for clopidogrel (Plavix)."
        }
    }
}