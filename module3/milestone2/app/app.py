from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import numpy as np
from typing import List

# Load model at startup (not per-request)
import os
from pathlib import Path

# Load model using absolute path
MODEL_PATH = Path(__file__).parent / "model.pkl"
model = joblib.load(MODEL_PATH)

# Create FastAPI app
app = FastAPI(
    title="Iris Classification API",
    description="ML model serving with FastAPI",
    version="1.0.0"
)

# Define request schema
class PredictionRequest(BaseModel):
    features: List[float] = Field(
        ...,
        example=[5.1, 3.5, 1.4, 0.2],
        description="Four features: sepal length, sepal width, petal length, petal width"
    )

# Define response schema
class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="Predicted class (0=setosa, 1=versicolor, 2=virginica)")
    class_name: str = Field(..., description="Class name")
    probabilities: List[float] = Field(..., description="Class probabilities")

@app.get("/")
def root():
    return {"message": "Iris Classification API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    # Convert input to numpy array
    features = np.array([request.features])
    
    # Make prediction
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0].tolist()
    
    # Map prediction to class name
    class_names = ["setosa", "versicolor", "virginica"]
    class_name = class_names[prediction]
    
    return {
        "prediction": prediction,
        "class_name": class_name,
        "probabilities": probabilities
    }