from catboost import CatBoostRegressor

# 1. Load the trained CatBoost model when FastAPI starts
try:
    cb_model = CatBoostRegressor()
    cb_model.load_model("geneweave_catboost.cbm")
except Exception as e:
    print(f"Warning: Could not load CatBoost model. {e}")

def run_expert_system(parsed_variants):
    """
    Takes parsed data from the VCF and asks the CatBoost model for a score.
    Example parsed_variants: {'CYP2C19': 'Poor', 'CYP2D6': 'Normal', ...}
    """
    
    # 2. Extract the raw text statuses in the EXACT order we trained them
    # We default to 'Normal' if a gene is missing from the VCF file
    features = [
        parsed_variants.get('CYP2C19', 'Normal'),
        parsed_variants.get('CYP2D6', 'Normal'),
        parsed_variants.get('DPYD', 'Normal'),
        parsed_variants.get('SLCO1B1', 'Normal')
    ]
    
    # 3. Ask CatBoost to predict the score based on the text!
    # CatBoost expects a 2D array, so we wrap features in brackets: [features]
    predicted_score = cb_model.predict([features])[0]
    
    # Ensure the score stays within your React dial's limits (0 to 99)
    final_score = min(max(round(predicted_score, 2), 0.0), 99.0)
    
    # 4. Generate the explainability trace for the React Dashboard
    reasons = [f"{gene} is {status}" for gene, status in parsed_variants.items() if status != 'Normal']
    
    if final_score >= 80:
        trace = f"CRITICAL RISK: ML Model detected severe pathway bottleneck. Contributing factors: {', '.join(reasons)}."
    elif final_score >= 40:
        trace = f"MODERATE RISK: ML Model detected metabolic impairment. Contributing factors: {', '.join(reasons)}."
    else:
        trace = "SAFE: ML Model predicts standard metabolism. Standard dosing recommended."

    # 5. Return EXACTLY what React and main.py expect
    return {
        "risk_score": final_score,
        "reasoning_trace": trace,
        "patient_profile": parsed_variants
    }