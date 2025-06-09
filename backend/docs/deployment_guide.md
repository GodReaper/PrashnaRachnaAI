# 🚀 Production Deployment Guide

This guide explains how to deploy your document processing application to production with cloud storage.

## 📋 Overview

Your application uses a **hybrid storage architecture**:
- **Development**: Files stored locally (`uploads/` folder)
- **Production**: Files stored in cloud storage (AWS S3, Google Cloud Storage, Azure Blob)
- **Database**: Metadata and processed content in PostgreSQL
- **Vector Store**: Embeddings in ChromaDB

## 🏗️ Architecture Comparison

### Development (Local Storage)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL     │    │   ChromaDB      │
│                 │    │   (metadata)     │    │   (vectors)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Local Uploads/  │
│ - pdf/          │
│ - docx/         │
│ - pptx/         │
└─────────────────┘
```

### Production (Cloud Storage)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL     │    │   ChromaDB      │
│   (on server)   │    │   (on server)    │    │   (on server)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Cloud Storage  │
│ AWS S3 / GCS /  │
│ Azure Blob      │
└─────────────────┘
```

## 🛠️ Deployment Options

### Option 1: AWS S3 (Recommended)

#### 1. Install Dependencies
```bash
pip install boto3==1.34.0
```

#### 2. Create S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://your-app-documents-bucket

# Set CORS configuration
aws s3api put-bucket-cors --bucket your-app-documents-bucket --cors-configuration file://cors.json
```

#### 3. Environment Variables
```bash
# .env (production)
FILE_STORAGE_TYPE=aws_s3
AWS_S3_BUCKET=your-app-documents-bucket
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

#### 4. IAM Policy (Recommended)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-app-documents-bucket/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::your-app-documents-bucket"
        }
    ]
}
```

### Option 2: Google Cloud Storage

#### 1. Install Dependencies
```bash
pip install google-cloud-storage==2.12.0
```

#### 2. Create GCS Bucket
```bash
# Using gcloud CLI
gsutil mb gs://your-app-documents-bucket
```

#### 3. Environment Variables
```bash
# .env (production)
FILE_STORAGE_TYPE=gcp
GCP_STORAGE_BUCKET=your-app-documents-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Option 3: Azure Blob Storage

#### 1. Install Dependencies
```bash
pip install azure-storage-blob==12.19.0
```

#### 2. Environment Variables
```bash
# .env (production)
FILE_STORAGE_TYPE=azure
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
AZURE_CONTAINER_NAME=documents
```

## 🌐 Platform-Specific Deployment

### Heroku
```bash
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# Config vars
heroku config:set FILE_STORAGE_TYPE=aws_s3
heroku config:set AWS_S3_BUCKET=your-bucket
heroku config:set AWS_ACCESS_KEY_ID=...
heroku config:set AWS_SECRET_ACCESS_KEY=...
```

### Railway
```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "web"
source = "."
```

### Render
```yaml
# render.yaml
services:
  - type: web
    name: prashna-rachna-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: FILE_STORAGE_TYPE
        value: aws_s3
      - key: AWS_S3_BUCKET
        value: your-bucket
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Don't create uploads directory in production
RUN rm -rf uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Migration Process

### From Local to Cloud Storage

1. **Backup Current Files**
```bash
tar -czf uploads_backup.tar.gz uploads/
```

2. **Upload Existing Files to Cloud**
```python
# migration_script.py
import os
from app.services.cloud_file_service import CloudFileStorageService

def migrate_to_cloud():
    cloud_service = CloudFileStorageService("aws_s3")
    
    for root, dirs, files in os.walk("uploads"):
        for file in files:
            local_path = os.path.join(root, file)
            # Extract user_id and file_type from path
            # Upload to cloud storage
```

3. **Update Environment**
```bash
# Switch to cloud storage
export FILE_STORAGE_TYPE=aws_s3
```

4. **Update Database Records**
```sql
-- Update file_path to cloud paths
UPDATE documents 
SET file_path = REPLACE(file_path, 'uploads/', 'documents/');
```

## 📊 Monitoring & Observability

### Storage Metrics
```python
# Add to your monitoring
def get_storage_metrics():
    if storage_type == "aws_s3":
        # Monitor S3 usage
        cloudwatch = boto3.client('cloudwatch')
        # Get metrics
    elif storage_type == "gcp":
        # Monitor GCS usage
        pass
```

### Cost Optimization
```python
# S3 Lifecycle Policy
lifecycle_config = {
    'Rules': [
        {
            'ID': 'document-lifecycle',
            'Status': 'Enabled',
            'Transitions': [
                {
                    'Days': 30,
                    'StorageClass': 'STANDARD_IA'
                },
                {
                    'Days': 90,
                    'StorageClass': 'GLACIER'
                }
            ]
        }
    ]
}
```

## 🔒 Security Considerations

### 1. Access Control
- Use IAM roles instead of access keys when possible
- Implement least-privilege principle
- Enable bucket encryption at rest

### 2. Network Security
- Configure CORS properly
- Use signed URLs for temporary access
- Implement rate limiting

### 3. Data Protection
```python
# Enable server-side encryption
s3_client.put_object(
    Bucket=bucket_name,
    Key=key,
    Body=content,
    ServerSideEncryption='AES256'
)
```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied**
```bash
# Check IAM permissions
aws sts get-caller-identity
aws s3 ls s3://your-bucket
```

2. **Import Errors**
```bash
# Install cloud dependencies
pip install boto3  # For AWS
pip install google-cloud-storage  # For GCP
pip install azure-storage-blob  # For Azure
```

3. **Temporary File Issues**
```python
# Check temp directory permissions
import tempfile
print(tempfile.gettempdir())
```

## 📈 Benefits of This Architecture

✅ **Scalability**: Handle unlimited file storage
✅ **Reliability**: Cloud provider SLAs and redundancy
✅ **Performance**: CDN integration possible
✅ **Cost-Effective**: Pay only for what you use
✅ **Security**: Enterprise-grade encryption and access control
✅ **Backup**: Automatic versioning and backup
✅ **Global**: Serve files from multiple regions

## 🎯 Next Steps

1. Choose your cloud provider
2. Set up bucket/container
3. Configure credentials
4. Update environment variables
5. Deploy and test
6. Monitor usage and costs

Your hybrid storage architecture is production-ready and follows industry best practices! 🚀 