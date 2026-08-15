import pandas as pd
import random

genes = ['CYP2C19', 'CYP2D6', 'DPYD', 'SLCO1B1']
statuses = ['Normal', 'Intermediate', 'Poor']
risk_weights = {'Normal': 10, 'Intermediate': 25, 'Poor': 40}

data = []

print("Generating 5,000 clinical records for CatBoost...")

for i in range(5000):
    patient = {'Patient_ID': f"P_{i+1}"}
    total_base_score = 0
    poor_count = 0
    
    for gene in genes:
        # 60% chance of Normal, 30% Intermediate, 10% Poor
        status = random.choices(statuses, weights=[0.6, 0.3, 0.1])[0]
        
        # Save the exact column name CatBoost is looking for!
        patient[f"{gene}_Text"] = status
        
        total_base_score += risk_weights[status]
        if status == 'Poor':
            poor_count += 1
            
    # Apply your GeneWeave Pathway Overlap Penalty
    if poor_count >= 2:
        final_score = total_base_score * 1.35 
    else:
        final_score = total_base_score
        
    patient['Target_Risk_Score'] = min(final_score, 99.0)
    data.append(patient)

# Save to the exact filename your training script is looking for
df = pd.DataFrame(data)
df.to_csv('real_genomic_training_data.csv', index=False)
print("✅ SUCCESS: Saved 'real_genomic_training_data.csv' to your backend folder!")