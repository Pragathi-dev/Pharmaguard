from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Import your existing custom modules
from parser import extract_variants  
from engine import run_expert_system

# Import the database collection we created in database.py
from database import reports_collection 

app = FastAPI()

# Add CORS Middleware so React can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (perfect for local development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_vcf(file: UploadFile = File(...)):
    # 1. Save uploaded file temporarily
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        # 2. Extract variants from the VCF (Returns our dictionary!)
        patient_variants = extract_variants(file_path)
        
        # 3. Run the ML Model Engine (CatBoost takes over here)
        analysis_results = run_expert_system(patient_variants)
        
        # 4. Save the generated report to MongoDB
        # We wrap the results in a structured document with a timestamp
        db_document = {
            "source_file": file.filename,
            "timestamp": datetime.utcnow(),
            "clinical_results": analysis_results  # This saves the entire generated ML output!
        }
        db_result = await reports_collection.insert_one(db_document)
        
        # Attach the MongoDB ID to the results so the React frontend knows it was saved
        analysis_results["database_record_id"] = str(db_result.inserted_id)
        analysis_results["database_status"] = "Successfully saved to MongoDB"
        
        return analysis_results
        
    finally:
        # Clean up temp file so your server doesn't get cluttered
        if os.path.exists(file_path):
            os.remove(file_path)