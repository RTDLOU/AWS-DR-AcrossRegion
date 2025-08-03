# 🌩️ AWS Disaster Recovery Across Regions (POC)

This project implements a disaster recovery strategy using AWS services across multiple regions with Route 53 failover, Lambda, S3 CRR, RDS (MySQL), Flask, and VPC Endpoints.

---

## 💡 Architecture

![Architecture](architecture.png)

<sub>_This image must be in the same folder as this file (e.g., uploaded to the root of your repo)._</sub>

---

## 🔁 Disaster Recovery Strategy

The application is designed for high availability and regional failover using AWS-native services.

### 🔹 Flask Web Server (EC2)
- Hosted in **Virginia region**
- Runs in a **public subnet**
- Handles front-end and triggers backend logic via Lambda

### 🔹 AWS Lambda
- Deployed in a **private subnet**
- Handles business logic, reads from **S3** and **RDS**
- Invoked by EC2 via Boto3

### 🔹 Amazon RDS (MySQL)
- Runs in a **private subnet**
- Configured for **Multi-AZ failover** in **Virginia**
- Has a **cross-region read replica** in **Oregon**

### 🔹 Amazon S3
- Stores content like `msgdrdct.txt`
- Enabled **Cross-Region Replication (CRR)** to Oregon bucket

### 🔹 Route 53
- Configured with **failover routing policy**
- **Primary endpoint:** EC2 in Virginia
- **Secondary endpoint:** Oregon region

---

### ⚠️ Failover Test (Manual Simulation)

- EC2 instance in **Virginia** was **stopped manually**
- **Route 53 automatically failed over** to secondary (Oregon)
- **Read replica in Oregon promoted to primary**
- Application continued running with minimal disruption

---

## 🧪 Lambda Function (Python)

```python
import json
import boto3
import pymysql
import os

s3 = boto3.client('s3')

rds_host = os.environ['RDS_HOST']
username = os.environ['DB_USERNAME']
password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    s3_bucket = os.environ['S3_BUCKET']
    s3_key = os.environ['S3_KEY']

    s3_object = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    s3_content = s3_object['Body'].read().decode('utf-8')

    connection = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)
    with connection.cursor() as cursor:
        cursor.execute("SELECT content FROM messages LIMIT 1")
        result = cursor.fetchone()
        rds_message = result[0]

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': f"<html><body><h1>{s3_content}</h1><h2>{rds_message}</h2></body></html>"
    }
```

---

## 🌐 Flask App on EC2

```python
from flask import Flask
import boto3

app = Flask(__name__)
lambda_client = boto3.client('lambda')

@app.route('/')
def index():
    response = lambda_client.invoke(
        FunctionName='ReadS3RDSData',
        InvocationType='RequestResponse'
    )
    return response['Payload'].read().decode('utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

---

## 📂 GitHub Folder Structure

```
AWS-DR-AcrossRegion/
├── index.md
├── architecture.png
├── lambda/
│   └── lambda_function.py
├── ec2/
│   └── app.py
├── scripts/
│   └── setup.sh
```

---

## 📘 Lessons Learned

### 🔧 Technical Learnings

- ✅ **Route 53 Failover Works Best with Health Checks**
  - Use EC2 health check or HTTP endpoint check for automatic failover
  - Manual EC2 stop simulates failure effectively in test

- ✅ **RDS Read Replica Promotion is Manual**
  - AWS does not auto-promote read replicas across regions
  - Manual intervention required to promote and point app to new DB

- ✅ **S3 CRR is Simple and Reliable**
  - Ensure bucket policies and IAM permissions are consistent in both regions

- ✅ **Lambda in Private Subnet Needs Internet Access**
  - Use NAT Gateway or S3 VPC Endpoint to allow Lambda to access S3 and external URLs

- ✅ **Flask EC2 Does Not Need to Be in Same Subnet as Lambda**
  - Communication is via AWS SDK (boto3), not direct networking

- ✅ **VPC Subnet Misconfigurations Can Block Deployments**
  - Missing route tables, NAT, or VPC endpoints can silently block subnet visibility

---

## 🧠 Architectural Best Practices

- Use **Private RDS + Lambda + S3 with Endpoint** as best practice
- Keep **Flask EC2** in public subnet for easy user access
- Use **SSM Parameter Store or Secrets Manager** for DB credentials
- Enable **logging in CloudWatch** for Lambda and Flask (EC2)

---

## 💵 Cost Awareness

- **NAT Gateway** is costly — consider replacing with **S3 VPC endpoint** when possible
- **Cross-region RDS replication** and storage incur additional cost
- Use **S3 lifecycle policies** to control storage costs in the secondary region
