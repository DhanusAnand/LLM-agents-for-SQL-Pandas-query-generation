from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
import json
import pandas as pd
from llm_agent import process_pandas_result_to_json, query_pandas_agent

allowed_hosts=["http://localhost:4200/*","http://localhost:4200"]

app = Flask(__name__)
CORS(app,origins=allowed_hosts)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Set your DynamoDB table name and S3 bucket name
DYNAMODB_TABLE_NAME = 'YourDynamoDBTableName'
USER_FILES_TABLE = "llm-user-files"
LLM_FILE_TABLE = "llm-file-table"
LLM_USER_TABLE = "llm-user-table"
S3_BUCKET_NAME = 'llm-query-generator'




# Route to get an upload pre-signed URL
@app.route('/generate-upload-url', methods=['GET'])
def generate_upload_url():
    try:
        filename = request.args.get('filename')
        params = {
            'Bucket': S3_BUCKET_NAME,
            'Key': filename,
            'ContentType': 'text/csv'
        }
        url = s3_client.generate_presigned_url('put_object', Params=params, ExpiresIn=600)
        return jsonify({'url': url})
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(e)
        return jsonify({'error': 'Credentials error'}), 500
    except Exception as e:
        print(e)
        return jsonify({'error': 'Error generating upload URL'}), 500

# Route to get pre-signed URL
@app.route('/generate-view-url', methods=['GET'])
def generate_view_url():
    try:
        filename = request.args.get('filename')
        params = {
            'Bucket': S3_BUCKET_NAME,
            'Key': filename
        }
        url = s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
        return jsonify({'url': url})
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(e)
        return jsonify({'error': 'Credentials error'}), 500
    except Exception as e:
        print("*"*100)
        print(e)
        return jsonify({'error': 'Error generating download URL'}), 500


@app.route('/get-pandas-query', methods=['POST'])
def get_pandas_query():
    # Get CSV file key and user query from the request
    data = request.json
    file_key = data.get('file_key')
    user_query = data.get('query')

    if not file_key or not user_query:
        return jsonify({'error': 'file_key and query are required'}), 400


    # Get the file from S3
    params = {
            'Bucket': S3_BUCKET_NAME,
            'Key': file_key
        }
    url = s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
    print(f'url: {url}')
    df = pd.read_csv(url)
    res = query_pandas_agent(df,user_query)
    llm_output = process_pandas_result_to_json(res)

    # Return the response back to the frontend
    return jsonify(llm_output), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
