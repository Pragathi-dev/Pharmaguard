import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split

print("Step 1: Loading Dataset...")
# This is the CSV you generated from your VCF folders
df = pd.read_csv('real_genomic_training_data.csv')

# Step 2: Separate Features and Target
# Notice we are using the TEXT columns, not numbers!
X = df[['CYP2C19_Text', 'CYP2D6_Text', 'DPYD_Text', 'SLCO1B1_Text']]
y = df['Target_Risk_Score']

# Tell CatBoost which columns are categories (all of them: indices 0, 1, 2, 3)
categorical_features_indices = [0, 1, 2, 3]

print("Step 3: Splitting Data (80% Train, 20% Test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Step 4: Training CatBoost Hybrid Model...")
# Initialize the model. We use silent=True to stop it from printing 1000 lines of math
model = CatBoostRegressor(iterations=200, depth=6, learning_rate=0.1, random_seed=42)

# Train the model, explicitly passing the categorical features
model.fit(X_train, y_train, cat_features=categorical_features_indices, verbose=False)

# Check accuracy
score = model.score(X_test, y_test)
print(f"-> Model R-squared Accuracy: {score:.4f}")

print("Step 5: Saving Model...")
# CatBoost has its own highly optimized save format
model.save_model("geneweave_catboost.cbm")
print("SUCCESS: Hybrid Model saved as 'geneweave_catboost.cbm'!")