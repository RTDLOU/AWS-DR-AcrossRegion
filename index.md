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
