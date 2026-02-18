# IDS 568 - Milestone 1: Web & Serverless Model Serving

**Student:** Josephine Chou 
**Course:** IDS 568 - Managing ML & AI Lifecycle  

## Overview

This project implements an Iris classification model deployed using two different serving patterns:
1. **Cloud Run** - Containerized FastAPI application
2. **Cloud Functions Gen2** - Serverless function deployment

The goal is to compare lifecycle characteristics, latency behavior, and reproducibility trade-offs between container-based and function-based ML serving.

## Deployed Services

### Cloud Run Deployment
- **URL:** https://iris-classifier-l4gdvrm7uq-uc.a.run.app
- **Swagger UI:** https://iris-classifier-l4gdvrm7uq-uc.a.run.app/docs
- **Container Image:** `us-central1-docker.pkg.dev/ids568-mlops/ml-models/iris-classifier:v1`
- **Runtime:** Python 3.13, FastAPI + Uvicorn
- **Memory:** 512Mi

### Cloud Function Deployment
- **URL:** https://us-central1-ids568-mlops.cloudfunctions.net/iris-predict
- **Runtime:** Python 3.12, functions-framework
- **Memory:** 512MB
- **Generation:** Gen2 (recommended by course materials)

## Project Structure
```
ids568-mlops-m1/
├── main.py                 # FastAPI application
├── model.pkl              # Trained Iris classifier (100% accuracy)
├── train_model.py         # Model training script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── .dockerignore         # Docker ignore rules
├── cloud_function/       # Cloud Function deployment
│   ├── main.py          # Function handler
│   ├── model.pkl        # Model copy
│   └── requirements.txt # Function dependencies
└── README.md            # This file
```

## Model Information

- **Dataset:** Iris (sklearn.datasets.load_iris)
- **Algorithm:** Random Forest Classifier (n_estimators=100)
- **Training Accuracy:** 100% on test set
- **Features:** 4 (sepal length, sepal width, petal length, petal width)
- **Classes:** 3 (setosa, versicolor, virginica)
- **Model Size:** 183 KB

## API Usage

### Request Format
```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

### Response Format
```json
{
  "prediction": 0,
  "class_name": "setosa",
  "probabilities": [1.0, 0.0, 0.0]
}
```

### Example Requests

**Cloud Run:**
```bash
curl -X POST "https://iris-classifier-l4gdvrm7uq-uc.a.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

**Cloud Function:**
```bash
curl -X POST "https://us-central1-ids568-mlops.cloudfunctions.net/iris-predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Performance Comparison

### Latency Measurements

| Metric | Cloud Run | Cloud Function Gen2 | Difference |
|--------|-----------|---------------------|------------|
| Cold Start | 0.300s | 7.589s | +7.3s (25x) |
| Warm (1st request) | 0.361s | 0.399s | +0.04s |
| Warm (2nd request) | 0.206s | 0.332s | +0.13s |
| **Average Warm** | **0.28s** | **0.37s** | **+0.09s** |

### Key Findings

1. **Cold Start Performance:**
   - Cloud Run is 25x faster (0.3s vs 7.6s)
   - Container startup is significantly faster than runtime initialization
   - Critical for user-facing applications

2. **Warm Instance Performance:**
   - Comparable performance (~0.3s range)
   - Both effectively cache the model in memory
   - Cloud Run marginally faster due to persistent container state

3. **Traffic Pattern Implications:**
   - High-frequency traffic: Cloud Run clear winner
   - Sporadic traffic: Both experience cold starts, cost matters more

## Lifecycle Analysis

### Cloud Run (Container-based)

**Advantages:**
- Full environment control (Dockerfile)
- Model loaded once at startup
- Multiple concurrent requests per instance
- Reproducible builds with image snapshots
- Faster cold starts

**Trade-offs:**
- More complex deployment (Docker required)
- Larger deployment artifact

### Cloud Functions (Function-based)

**Advantages:**
- Simple deployment (source code only)
- Event-driven triggers available
- Managed runtime (less operational overhead)
- Automatic scaling per request

**Trade-offs:**
- Slower cold starts (7.6s)
- Limited concurrency (1 request/instance in Gen2 default)
- Less environment control
- Dependent on GCP runtime updates

## Reproducibility Considerations

### Cloud Run
- **Dockerfile** provides complete environment specification
- Exact Python version, system dependencies, package versions
- Image registry maintains immutable snapshots
- Can rebuild identical environment months later

### Cloud Functions
- **requirements.txt** specifies Python packages
- Python runtime managed by GCP (less control)
- Simpler but less reproducible over time
- Runtime updates may affect behavior

**Verdict:** Cloud Run offers superior reproducibility for production ML systems.

## Deployment Instructions

### Prerequisites
```bash
# GCP CLI authenticated
gcloud auth login

# Project configured
gcloud config set project ids568-mlops
gcloud config set run/region us-central1
```

### Cloud Run Deployment
```bash
# Build and push Docker image
docker build -t iris-classifier:local .
docker tag iris-classifier:local \
  us-central1-docker.pkg.dev/ids568-mlops/ml-models/iris-classifier:v1
docker push us-central1-docker.pkg.dev/ids568-mlops/ml-models/iris-classifier:v1

# Deploy to Cloud Run
gcloud run deploy iris-classifier \
  --image=us-central1-docker.pkg.dev/ids568-mlops/ml-models/iris-classifier:v1 \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi
```

### Cloud Function Deployment
```bash
# Deploy Gen2 function
gcloud functions deploy iris-predict \
  --runtime=python312 \
  --region=us-central1 \
  --source=./cloud_function \
  --entry-point=predict \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --gen2
```

## Use Case Recommendations

### Choose Cloud Run when:
- Latency SLA < 500ms required
- High traffic volume (cost-effective instance reuse)
- Model size > 100MB
- Custom system dependencies needed
- Production deployment requiring reproducibility

### Choose Cloud Functions when:
- Sporadic traffic (optimize for cost)
- Simple Python-only dependencies
- Event-driven architecture (Pub/Sub, Cloud Storage triggers)
- Rapid prototyping and development
- Microservices with simple serving logic

## Lessons Learned

1. **Cold start optimization is critical** for production ML serving
2. **Container-based deployment** provides better control and performance
3. **Function-based deployment** offers simplicity at a latency cost
4. **The "best" pattern depends on traffic characteristics** and requirements
5. **Reproducibility** requires investment in infrastructure-as-code

## Technologies Used

- **ML Framework:** scikit-learn 1.8.0
- **Web Framework:** FastAPI 0.128.0 (Cloud Run), functions-framework 3.5.0 (Cloud Functions)
- **Containerization:** Docker
- **Cloud Platform:** Google Cloud Platform
  - Cloud Run
  - Cloud Functions Gen2
  - Artifact Registry
  - Cloud Build

## Author

**Josephine Chou** 
---