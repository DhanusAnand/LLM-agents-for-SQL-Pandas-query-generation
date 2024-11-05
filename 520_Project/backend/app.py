from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import requests
import json

app = Flask(__name__)
CORS(app)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Set your DynamoDB table name and S3 bucket name
DYNAMODB_TABLE_NAME = 'YourDynamoDBTableName'
S3_BUCKET_NAME = 'YourS3BucketName'
LLM_API_URL = 'https://api.your-llm.com/generate'  # Change this to your LLM API endpoint

@app.route('/upload', methods=['POST'])
def upload():
    # Get CSV file key and user query from the request
    data = request.json
    file_key = data.get('file_key')
    user_query = data.get('query')

    if not file_key or not user_query:
        return jsonify({'error': 'file_key and query are required'}), 400

    # Get file metadata from DynamoDB
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    metadata_response = table.get_item(Key={'file_key': file_key})
    
    if 'Item' not in metadata_response:
        return jsonify({'error': 'File not found'}), 404
    
    file_metadata = metadata_response['Item']

    # Get the file from S3
    try:
        s3_response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=file_key)
        file_content = s3_response['Body'].read().decode('utf-8')  # Assuming it's a text-based CSV
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Prepare the prompt for the LLM
    llm_input = {
        'metadata': file_metadata,
        'query': user_query,
        'file_content': file_content
    }

    # Call the LLM API
    llm_response = requests.post(LLM_API_URL, json=llm_input)

    if llm_response.status_code != 200:
        return jsonify({'error': 'LLM request failed', 'details': llm_response.text}), 500

    llm_output = llm_response.json()

    # Return the response back to the frontend
    return jsonify(llm_output), 200

if __name__ == '__main__':
    app.run(debug=True)
