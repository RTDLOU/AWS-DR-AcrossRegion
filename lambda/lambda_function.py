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
