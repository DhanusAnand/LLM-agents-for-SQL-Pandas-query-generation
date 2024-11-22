from flask import Blueprint, Flask, jsonify, request, redirect
from flask_classful import FlaskView, route
from flask_cors import cross_origin
from flask import make_response, request, current_app
from datetime import timedelta, datetime
from functools import update_wrapper
from models import *
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)

allowed_hosts=["http://localhost:4200/*","http://localhost:4200"]

# class LLMResource(FlaskView)

class UserResource(FlaskView):
    route_base = '/api/user/'

    @route('files', methods=['GET','POST','OPTIONS'])
    def get_user_files(self):
        return jsonify({
            'user': "test",
            "files": ['a.txt','b.txt']
        })

class ApiResource(FlaskView):
    route_base = '/'

    @route('hello', methods=['GET', 'POST', 'OPTIONS'])
    def health_check(self):
        return jsonify({'hello': "hello"})
    
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