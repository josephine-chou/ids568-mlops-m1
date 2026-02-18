# Iris Classification ML Service

![Build Status](https://github.com/josephine-chou/ids568-mlops-m1/actions/workflows/build.yml/badge.svg?branch=main)

Containerized machine learning inference service for Iris flower classification using FastAPI and scikit-learn.

## Features

- FastAPI-based REST API
- Multi-stage Docker build for optimized image size
- Automated CI/CD pipeline with GitHub Actions
- Comprehensive testing with pytest
- Production-ready containerization

## Quick Start

### Pull and Run the Docker Image
```bash
# Pull the latest image
docker pull us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mlops-course/iris-service:latest

# Run the container
docker run -d -p 8080:8080 --name iris-api us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mlops-course/iris-service:latest

# Test the API
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

### Local Development
```bash
# Clone the repository
git clone https://github.com/josephine-chou/ids568-mlops-m1.git
cd ids568-mlops-m1/module3/milestone2

# Build locally
docker build -t iris-service:local .

# Run locally
docker run -d -p 8080:8080 --name iris-local iris-service:local

# Run tests
pip install pytest httpx
pytest tests/ -v
```

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /predict` - Make predictions

### Example Request
```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

### Example Response
```json
{
  "prediction": 0,
  "class_name": "setosa",
  "probabilities": [0.97, 0.02, 0.01]
}
```

## Project Structure
```
module3/milestone2/
├── .github/workflows/
│   └── build.yml          # CI/CD pipeline
├── app/
│   ├── app.py            # FastAPI application
│   ├── model.pkl         # Trained ML model
│   └── requirements.txt  # Python dependencies
├── tests/
│   └── test_app.py       # Unit tests
├── Dockerfile            # Multi-stage build
├── README.md             # This file
└── RUNBOOK.md            # Operations guide
```

## CI/CD Pipeline

The project uses GitHub Actions for automated testing and deployment:

1. **Test Job**: Runs pytest on every push
2. **Build Job**: Builds Docker image on version tags
3. **Push Job**: Pushes to GCP Artifact Registry

Triggered by pushing version tags: `git tag v1.0.0 && git push --tags`

## Technology Stack

- **Framework**: FastAPI 0.128.0
- **ML Library**: scikit-learn 1.8.0
- **Container**: Docker with multi-stage builds
- **CI/CD**: GitHub Actions
- **Registry**: GCP Artifact Registry
- **Testing**: pytest

## Version History

- v1.0.0 - Initial containerized release

## Documentation

See [RUNBOOK.md](RUNBOOK.md) for detailed operational procedures.

## License

Educational project for IDS 568 - MLOps Course