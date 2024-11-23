import pandas as pd
from flask import Blueprint, Flask, jsonify, request, redirect
from flask_classful import FlaskView, route
# from flask_cors import cross_origin
# from flask import make_response, request, current_app
# from datetime import timedelta, datetime
# from functools import update_wrapper
from models import *
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from llm_agent import process_pandas_result_to_json, query_pandas_agent
from app.Api.models import *
from app.Api.exceptions import *
from app.Api.enums import *

allowed_hosts=["http://localhost:4200/*","http://localhost:4200"]

class UserResource(FlaskView):
    route_base = '/api/user/'
    # route_base = '/'

    @route('all/files', methods=['GET','POST'])
    def get_user_files(self):
        user = User.get(request.args.get('user_id'))
        return jsonify(UserFiles.get(user.user_id))
    
    @route('upload/file', methods=['POST'])
    def upload_file(self):
        return jsonify({

        })
    
    @route('generate-upload-url', methods=['GET'])
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

    # @route('view/file-url', methods=['GET'])
    @route('generate-view-url', methods=['GET'])
    def generate_view_url():
        try:
            filename = request.json.get('filename')
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

    
    @route('delete/file')
    def delete_file(self):
        return jsonify({

        })
    
class AuthResource(FlaskView):
    route_base = '/'

    @route('hello', methods=['GET', 'POST', 'OPTIONS'])
    def health_check(self):
        return jsonify({'hello': "hello"})
    
    # @route('register', methods=['POST'])
    # def register(self):
    #     '''
    #     Register a new user
    #     '''
    #     try:
    #         data = request.json # data.keys = ('username', 'name', 'email')
    #         # check if the user already exists
    #         user = User.get(data['username'])
    #         if user is not None:
    #             raise UserAlreadyExistsException(user.username)
            
    #         user, status = User.validate_nd_make_user(data)
    #         if status==Status.VALID:
    #             user.put()
    #     except InvalidInputException as e:
    #         print(f"error: {e}")
    #         return jsonify({
    #             "msg": e.message
    #         }),200
    #     except UserAlreadyExistsException as e:
    #         print(f"error: {e}")
    #         return jsonify({
    #             "msg": e.message
    #         })
    #     except Exception as e:
    #         print(f"error: {e}")
    #         return jsonify({
    #             "msg": f"{e}"
    #         })
        
    
    @route('login', methods=['POST'])
    def login(self):
        user_id = request.json.get('user_id')
        password = request.json.get('password')
        try: 
            resp = User.get(user_id)
            print(resp)
            if resp['password']==password:
                access_token = create_access_token(identity=user_id)
                print(access_token)
                response = jsonify({"msg": "Login successful"})
                set_access_cookies(response, access_token)  # Set JWT token as a cookie
                return response, 200
            else:
                return jsonify({"msg": "Bad username or password"}), 401
        except Exception as e:
            print("error....",e)
            return jsonify({"msg": "Bad username or password"}), 401
    
    @route('auth_check', methods=['GET'])
    @jwt_required()
    def auth_check(self):
        current_user = get_jwt_identity()
        return jsonify(logged_in=True, user_id=current_user), 200

    @route("/logout", methods=["POST"])
    @jwt_required()
    def logout(self):
        response = jsonify({"msg": "Logout successful"})
        unset_jwt_cookies(response)  # Clear JWT cookies
        return response, 200
    
# This contains the business logic apis
class ApiResource(FlaskView):
    route_base = '/'

    @route('get-pandas-query', methods=['POST'])
    @jwt_required()
    def get_pandas_query(self):
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