# app.py

from fastapi import FastAPI
from fetch_latest import fetch_latest_record
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend requests
origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def read_root():
    return {"message": "Forex Prediction System API is running!"}


@app.get("/get_latest")
def get_latest_data():
    """Fetch the latest real-time forex record and append to CSV."""
    try:
        latest_data = fetch_latest_record()
        if latest_data:
            return latest_data
        else:
            return {"error": "No data fetched from API"}

    except Exception as e:
        return {"error": str(e)}
