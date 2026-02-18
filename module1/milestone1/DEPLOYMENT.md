# Deployment Guide

## Prerequisites

1. **Google Cloud Account**
   - Active GCP project
   - Billing enabled
   - APIs enabled: Cloud Run, Cloud Functions, Artifact Registry, Cloud Build

2. **Local Tools**
```bash
   # Required installations
   - Python 3.12+
   - Docker Desktop
   - Google Cloud SDK (gcloud CLI)
```

3. **Authentication**
```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud config set run/region us-central1
```

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/josephine-chou/ids568-mlops-m1.git
cd ids568-mlops-m1
```

### 2. Train Model Locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install scikit-learn numpy joblib
python train_model.py
```

### 3. Test Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Test at http://localhost:8000/docs
```

### 4. Deploy to Cloud Run
```bash
# Set environment variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Create Artifact Registry
gcloud artifacts repositories create ml-models \
    --repository-format=docker \
    --location=$REGION

# Build and push
docker build -t iris-classifier:local .
docker tag iris-classifier:local \
    ${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-models/iris-classifier:v1
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-models/iris-classifier:v1

# Deploy
gcloud run deploy iris-classifier \
    --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-models/iris-classifier:v1 \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --memory=512Mi
```

### 5. Deploy Cloud Function
```bash
gcloud functions deploy iris-predict \
    --runtime=python312 \
    --region=$REGION \
    --source=./cloud_function \
    --entry-point=predict \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512MB \
    --gen2
```

## Troubleshooting

### Docker Build Issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t iris-classifier:local .
```

### Cloud Run Deployment Issues
```bash
# Check service logs
gcloud run services logs read iris-classifier --region=$REGION

# Verify image exists
gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/ml-models
```

### Cloud Function Issues
```bash
# Check function logs
gcloud functions logs read iris-predict --region=$REGION --gen2

# Redeploy
gcloud functions delete iris-predict --region=$REGION --gen2 --quiet
# Then deploy again
```

## Monitoring

### Cloud Run
```bash
# View service details
gcloud run services describe iris-classifier --region=$REGION

# Monitor requests
# Visit: https://console.cloud.google.com/run
```

### Cloud Functions
```bash
# View function details
gcloud functions describe iris-predict --region=$REGION --gen2

# Monitor invocations
# Visit: https://console.cloud.google.com/functions
```

## Cost Optimization

- Both services use **scale-to-zero** (no cost when idle)
- Cloud Run free tier: 2M requests/month
- Cloud Functions free tier: 2M invocations/month
- Artifact Registry: 0.5GB storage free

## Cleanup
```bash
# Delete Cloud Run service
gcloud run services delete iris-classifier --region=$REGION --quiet

# Delete Cloud Function
gcloud functions delete iris-predict --region=$REGION --gen2 --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete ml-models --location=$REGION --quiet

# Delete Docker images locally
docker rmi iris-classifier:local
docker rmi ${REGION}-docker.pkg.dev/${PROJECT_ID}/ml-models/iris-classifier:v1
```
EOF
```