# Actus - ML Deployment Repository

Actus is a comprehensive ML deployment repository for deploying V-JEPA-2 models necessary for Intentus and Perceptus projects. This repository provides multiple deployment options including AWS Lambda, Modal Labs, and local Docker environments.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker
- AWS CLI (for Lambda deployment)
- Modal CLI (for Modal Labs deployment)

### Environment Setup
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your configuration:
   ```bash
   # Model Configuration
   MODEL_NAME=facebook/vjepa2-vitg-fpc64-256
   MODEL_PATH=/path/to/your/model/weights
   CLASSIFIER_PATH=/path/to/your/classifier/weights
   
   # AWS Configuration (for Lambda)
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   
   # Modal Configuration
   MODAL_TOKEN_ID=your_modal_token
   MODAL_TOKEN_SECRET=your_modal_secret
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   WORKERS=1
   ```

## 📁 Project Structure

```
actus/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vjepa2_model.py
│   │   └── classifier.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   └── utils/
│       ├── __init__.py
│       ├── image_processing.py
│       └── video_processing.py
├── deployments/
│   ├── lambda/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── handler.py
│   ├── modal/
│   │   ├── app.py
│   │   └── requirements.txt
│   └── docker/
│       ├── Dockerfile
│       └── docker-compose.yml
├── tests/
│   ├── __init__.py
│   ├── test_model.py
│   └── test_api.py
├── scripts/
│   ├── build_lambda.sh
│   ├── deploy_modal.sh
│   └── run_local.sh
├── requirements.txt
├── .env.example
└── README.md
```

## 🐳 Local Docker Deployment

### Build and Run
```bash
# Build the Docker image
docker build -f deployments/docker/Dockerfile -t actus-ml .

# Run with docker-compose
docker-compose -f deployments/docker/docker-compose.yml up -d

# Or run directly
docker run -p 8000:8000 --env-file .env actus-ml
```

### Test the API
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_data"
  }'
```

## ☁️ AWS Lambda Deployment

### Build Lambda Package
```bash
# Build the Lambda deployment package
./scripts/build_lambda.sh
```

### Deploy to Lambda
```bash
# Create the function
aws lambda create-function \
  --function-name vjepa2-analyzer \
  --runtime provided.al2023 \
  --handler bootstrap \
  --architectures arm64 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --zip-file fileb://deployments/lambda/function.zip

# Update function code
aws lambda update-function-code \
  --function-name vjepa2-analyzer \
  --zip-file fileb://deployments/lambda/function.zip
```

## 🚀 Modal Labs Deployment

### Deploy to Modal
```bash
# Install Modal CLI
pip install modal

# Authenticate
modal token new

# Deploy the application
./scripts/deploy_modal.sh
```

### Access Modal Endpoint
The Modal deployment will provide a public endpoint URL that you can use in your client applications.

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Test API Endpoints
```bash
# Test local deployment
curl -X POST http://localhost:8000/health

# Test with sample image
python scripts/test_api.py
```

## 📊 API Documentation

### Endpoints

#### POST /analyze
Analyze an image for visual intention using V-JEPA-2.

**Request:**
```json
{
  "image_data": "base64_encoded_image_data",
  "goal_image": "base64_encoded_goal_image" // optional
}
```

**Response:**
```json
{
  "predicted_action": "string",
  "confidence": 0.95,
  "has_intention": true,
  "intention_type": "visual_action",
  "description": "V-JEPA-2 predicted action: reaching",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_NAME` | HuggingFace model name | `facebook/vjepa2-vitg-fpc64-256` |
| `MODEL_PATH` | Path to local model weights | `/models/vjepa2_weights.pt` |
| `CLASSIFIER_PATH` | Path to classifier weights | `/models/classifier_weights.pt` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `WORKERS` | Number of workers | `1` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in the `/docs` folder
- Review the example implementations in `/examples`
