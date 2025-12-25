# Deployment Guide - Azure

## Prerequisites
- Azure subscription
- Azure CLI installed
- Docker installed
- OpenAI API key

## Deploy to Azure Container Instances

### 1. Create Azure resources

```bash
# Set variables
RESOURCE_GROUP="genai-chatbot-rg"
REGISTRY_NAME="genairegistry"
CONTAINER_NAME="genai-chatbot"
IMAGE_NAME="genai-enterprise-chatbot"

# Create resource group
az group create --name $RESOURCE_GROUP --location eastus

# Create container registry
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic
```

### 2. Build and push Docker image

```bash
# Login to registry
az acr login --name $REGISTRY_NAME

# Build image
az acr build --registry $REGISTRY_NAME --image $IMAGE_NAME:latest .

# Get login server
LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --query loginServer --output tsv)
```

### 3. Deploy container

```bash
# Get registry credentials
REGISTRY_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username --output tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value --output tsv)

# Deploy container instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image "$LOGIN_SERVER/$IMAGE_NAME:latest" \
  --registry-login-server $LOGIN_SERVER \
  --registry-username $REGISTRY_USERNAME \
  --registry-password $REGISTRY_PASSWORD \
  --ports 5000 \
  --environment-variables \
    AZURE_OPENAI_API_KEY=your_key \
    AZURE_OPENAI_ENDPOINT=your_endpoint \
    AZURE_DEPLOYMENT_NAME=gpt-35-turbo \
    SECRET_KEY=your_secret_key \
  --memory 2 \
  --cpu 1
```

### 4. Access the application

```bash
# Get container IP
CONTAINER_IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.ip --output tsv)
echo "Application available at: http://$CONTAINER_IP:5000"
```

## Deploy to AWS (ECS)

### 1. Create ECR repository

```bash
aws ecr create-repository --repository-name genai-chatbot --region us-east-1
```

### 2. Build and push image

```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag genai-chatbot:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/genai-chatbot:latest

# Push image
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/genai-chatbot:latest
```

### 3. Create ECS task definition and service

See `ecs-task-definition.json`

## Environment Variables

Create `.env` file with:

```
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-35-turbo
SECRET_KEY=your-secret-key-change-in-production
PORT=5000
DOCUMENT_PATH=data/sample_docs
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
CORS_ORIGINS=*
```

## Health Check

```bash
curl http://your-container-ip:5000/health
```

## Monitoring

Monitor logs and metrics through Azure Portal or CloudWatch
