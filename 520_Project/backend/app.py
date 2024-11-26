# TODO: File to be removed
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
import json
import pandas as pd
from llm_agent import process_pandas_result_to_json, query_pandas_agent

allowed_hosts=["http://localhost:4200/*","http://localhost:4200"]

app = Flask(__name__)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 9000  # in seconds (900 seconds = 150 minutes)
app.config['JWT_SECRET_KEY'] = 'super_secret_key'
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production for HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Can enable for CSRF protection

jwt = JWTManager(app)


CORS(app, supports_credentials=True, origins=allowed_hosts)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Set your DynamoDB table name and S3 bucket name
DB = boto3.resource('dynamodb')
USER_FILES_TABLE = "llm-user-files"
LLM_FILE_TABLE = "llm-file-table"
USER_TABLE = DB.Table("llm-user-table")
S3_BUCKET_NAME = 'llm-query-generator'


@app.route('/login', methods=['POST'])
def login():
    user_id = request.json.get('user_id')
    password = request.json.get('password')
    try: 
        resp = USER_TABLE.get_item(
            Key = {
                'user_id':user_id
            }
        )
        print(resp)
        if resp['Item']['password']==password:
            access_token = create_access_token(identity=user_id)
            print(access_token)
            response = jsonify({"msg": "Login successful"})
            set_access_cookies(response, access_token)  # Set JWT token as a cookie
            return response, 200
        else:
            return jsonify({"msg": "Bad username or password"}), 401
    except:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/auth_check', methods=['GET'])
@jwt_required()
def auth_check():
    current_user = get_jwt_identity()
    return jsonify(logged_in=True, user_id=current_user), 200

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)  # Clear JWT cookies
    return response, 200

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
@jwt_required()
def get_pandas_query():
    user_id=get_jwt_identity()
    print(user_id)
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
