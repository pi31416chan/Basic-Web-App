# Imports
from flask import (
    request,
    current_app
)
from flask_restful import (
    Resource,
    Api
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from hmac import compare_digest
from .helper_func import (
    generate_uuid_b64,
    parse_auth_header,
    Token
)
from .db import (
    APIKey,
    db,
    User,
    APIKey
)



# Functions
def required_api_auth(func):

    def decorated(self,*args,**kwargs):
        auth = request.headers.get('Authorization')

        # Check if api_key is attached in the request
        if auth:
            api_key = parse_auth_header(auth)
            api_instance = APIKey.query.filter_by(
                               key=api_key).first()

            # Check if the api key provided is valid
            if api_instance:

                # Check if the api key provided is active
                if api_instance.active:
                    return func(self,*args,**kwargs)
                else:
                    return {"message":"Api key is invalid"},401
                
            else:
                return {"message":"Api key is invalid"},401
            
        else:
            return {
                "message":"Authorised api key is required for this request"
            },401

    return decorated

def required_admin_api_auth(func):

    def decorated(self,*args,**kwargs):
        auth = request.headers.get('Authorization')

        # Check if api_key is attached in the request
        if auth:
            api_key = parse_auth_header(auth)
            admin_api_instance = APIKey.query.filter_by(
                                    device_name="admin").first()

            # Check if the api key provided is valid
            key_correct = compare_digest(admin_api_instance.key,
                                         api_key)
            is_active = admin_api_instance.active
            if key_correct and is_active:
                    return func(self,*args,**kwargs)
            else:
                return {"message":"Api key is invalid"},401
        else:
            return {
                "message":"Authorised api key is required for this request"
            },401

    return decorated



# Extension Initialization
api = Api()



# Api Class Definition
class CheckPassword(Resource):
    @required_api_auth
    def post(self):
        data = request.get_json()

        # Check username & email existence
        user = User.query.filter_by(username=data.get('username')).first()
        if user:
            is_pw_correct = check_password_hash(user.password_hash,
                                                data.get('password'))
            if is_pw_correct:
                # Create token with one day validity 
                token = Token(
                    user_agent=request.headers.get('User-Agent'),
                    expiry=current_app.config['TOKEN_EXPIRY']
                )
                return {
                    "is_pw_correct":is_pw_correct,
                    "message":"Username and password correct",
                    "token": token.string()
                },200
            else:
                return {"message":"Username or password is invalid"},601
        else:
            return {
                "message":"Username or password is invalid"},601

class RegisterUser(Resource):
    @required_api_auth
    def post(self):
        data = request.get_json()

        # Check username & email existence
        username_exist = User.query.filter_by(username=data.get('username')).first()
        email_exist = User.query.filter_by(email=data.get('email')).first()
        if username_exist:
            return {"message":"Username is already used"},602
        elif email_exist:
            return {"message":"Email is already registered"},602
        else:
            user = User(username=data.get('username'),
                        email=data.get('email'),
                        password_hash=generate_password_hash(
                            data.get('password'),
                            salt_length=16))
            db.session.add(user)
            db.session.commit()
            return {
                "message":
                f"Successfully created user '{user.username}'."
            },201

class GenerateAPIKey(Resource):
    '''
    This API can generate API Key without authentication and write to the
    relevant database.
    
    This is only allowed for learning purposes, we should avoid doing this 
    in actual case and try to exclude the generation of API Key out of the 
    application itself.

    Expected Data:
    {
        "device_name": <device_name>
    }

    <device_name>: str (less than 50 characters)
    '''
    @required_admin_api_auth
    def post(self):
        data = request.get_json()

        # Check if device name is used
        device_exist = APIKey.query.filter_by(
                           device_name=data.get('device_name')).first()

        if device_exist:
            return {"message":"Device name is already used"},603
        else:
            # Avoid api key collision
            key_exist = True
            while key_exist:
                # Generate api key and store to database
                api_key = generate_uuid_b64()
                # Check api key collision
                key_exist = APIKey.query.filter_by(
                                key=api_key).first()
            else:
                api_instance = APIKey(key=api_key,
                                      device_name=data.get('device_name'))
                db.session.add(api_instance)
                db.session.commit()
                return {"api_key":api_key},200

class ValidateToken(Resource):
    @required_api_auth
    def get(self):
        if request.cookies.get('token'):
            token = Token(request.cookies['token'])
            return {
                "is_token_valid":token.validate()
            },200
        else:
            return {
                "is_token_valid":False
            },200

class TestApiAuth(Resource):
    def get(self):
        token = Token(user_agent=request.user_agent.string)
        return {"test":"success",
        "token":token.string()},200

    @required_api_auth
    def post(self):
        return {"test":"success"},200



# Routing
api.add_resource(CheckPassword,'/checkpassword')
api.add_resource(RegisterUser,'/registeruser')
api.add_resource(GenerateAPIKey,'/generateapikey')
api.add_resource(TestApiAuth,'/testapiauth')
api.add_resource(ValidateToken,'/validatetoken')