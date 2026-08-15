from motor.motor_asyncio import AsyncIOMotorClient

# Use the IP that worked in Compass
MONGO_URL = "mongodb://127.0.0.1:27017"

client = AsyncIOMotorClient(MONGO_URL)

# This will create a database named 'geneweave_db' automatically 
# the first time you save something.
db = client.geneweave_db

# These are your collections (like SQL tables)
reports_collection = db.get_collection("risk_reports")
patients_collection = db.get_collection("patient_data")