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
