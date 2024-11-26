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
import pyotp
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

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    data = request.json
    print(data)
    google_id = data.get('google_id')  # Check if signing up with Google

    user_id = data.get('email')
    print("UserID++++>")
    print(user_id)
    # Check if user already exists
    response = USER_TABLE.get_item(Key={'user_id': user_id})
    if 'Item' in response:
        print("Yes")
        return jsonify({'error': 'User already exists'}), 400
    else:
        print("No")
        # If Google ID is present, skip password requirement
        if google_id:
            user_id = google_id
        else:
            user_id = data['user_id']
            if not data.get('password'):
                return jsonify({"msg": "Password required for non-Google signups"}), 400

        # Save the user to DynamoDB
        try:
            pushResp = USER_TABLE.put_item(
                Item={
                    'user_id': user_id,
                    'email': data['email'],
                    'first_name': data['firstName'],
                    'last_name': data['lastName'],
                    'password': data.get('password', ''),  # Only required for non-Google signups
                }
            )
            print(pushResp)
            return jsonify({"msg": "Signup successful"}), 201
        except Exception as e:
            return jsonify({"msg": "Error saving user", "error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    data = request.json
    google_id = data.get('google_id')  # Check if logging in with Google

    # Fetch user from DynamoDB
    try:
        if google_id:
            response = USER_TABLE.get_item(Key={'user_id': google_id})
        else:
            response = USER_TABLE.get_item(Key={'user_id': data['email']})

        user = response.get('Item')

        if not user:
            return jsonify({"msg": "User not found"}), 404

        if not google_id and user['password'] != data.get('password'):
            return jsonify({"msg": "Invalid password"}), 401

        # Generate JWT token
        access_token = create_access_token(identity=user['email'])
        return jsonify({"msg": "Login successful", "token": access_token, "name": f"{user['first_name']} {user['last_name']}"}), 200

    except Exception as e:
        return jsonify({"msg": "Error logging in", "error": str(e)}), 500


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


#This endpoint retrieves the user's first and last name from the DynamoDB USER_TABLE
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Fetch the logged-in user's name"""
    user_email = get_jwt_identity()

    try:
        response = USER_TABLE.get_item(Key={'user_id': user_email})
        user = response.get('Item')

        if not user:
            return jsonify({"msg": "User not found"}), 404

        return jsonify({"name": f"{user['first_name']} {user['last_name']}"}), 200

    except Exception as e:
        return jsonify({"msg": "Error fetching user info", "error": str(e)}), 500


#This endpoint retrieves all files uploaded by the user, stored in the USER_FILES_TABLE
@app.route('/get-user-files', methods=['GET'])
@jwt_required()
def get_user_files():
    """Fetch the user's files"""
    user_email = get_jwt_identity()

    try:
        # Query DynamoDB for user's files
        response = dynamodb.Table(USER_FILES_TABLE).query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_email)
        )
        files = response.get('Items', [])

        return jsonify({"files": files}), 200

    except Exception as e:
        return jsonify({"msg": "Error fetching user files", "error": str(e)}), 500



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

# Testing Backend fetch
@app.route('/get-users-files', methods=['GET'])
@jwt_required()
def get_users_files(user_id):
    file_output = [ { "user_id": "a@gmail.com", "file_name": "file1.csv" }, { "user_id": "a@gmail.com", "file_name": "file2.csv" }, { "user_id": "a@gmail.com", "file_name": "file3.csv" } ]
    return jsonify(file_output), 200
    # try:
    #     # Query the llm-user-files table by user_id
    #     response = LLM_FILE_TABLE.query(
    #         KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
    #     )

    #     # Check if there are any files found
    #     files = response.get('Items', [])
    #     if not files:
    #         print(f"No files found for user_id: {user_id}")
    #     else:
    #         print(f"Files uploaded by user_id {user_id}:")
    #         for file in files:
    #             print(f"File ID: {file['file_id']}, File Name: {file['file_name']}, Upload Date: {file['upload_date']}")

    # except Exception as e:
    #     print(f"An error occurred: {e}")



if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
