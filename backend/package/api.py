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
    User
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
                    return (
                        {"message":"Api key is invalid"},
                        401
                    )
                
            else:
                return (
                    {"message":"Api key is invalid"},
                    401
                )
            
        else:
            return (
                {"message":"Authorized api key is required for this request"},
                401
            )

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
                return (
                    {"message":"Api key is invalid"},
                    401
                )
        else:
            return (
                {"message":"Authorized api key is required for this request"},
                401
            )

    return decorated



# Extension Initialization
api = Api()



# Api Class Definition
class CheckPassword(Resource):
    '''
    Check if the passed in credentials are correct.

    Expected JSON Data Format:
    ----------
    header = {
        "User-Agent":"XXXXX",
        "Authorization":"API_KEY XXXXXXXXXXXXXXXXXXXXXX"
    }
    data = {
        "username":"XXXXX",
        "password":"XXXXXXXXXXXXXXXXXXXXXX"
    }

    Returns:
    -----------
    If credentials correct:
        status_code = 200
        data = {
            'is_pw_correct': True,
            'message': 'Username and password correct',
            'token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'}
    Else:
        status_code = 601
        data = {"message": "Username or password is invalid"}
    '''
    @required_api_auth
    def post(self):
        data = request.get_json()

        # Check username existence
        user = User.query.filter_by(username=data.get('username')).first()
        if user:
            is_pw_correct = check_password_hash(user.password_hash,
                                                data.get('password'))
            if is_pw_correct:
                # Create token 
                token = Token(
                    user_agent=request.headers.get('User-Agent'),
                    expiry=current_app.config['TOKEN_EXPIRY'],
                )
                return (
                    {
                        "is_pw_correct":is_pw_correct,
                        "message":"Username and password correct",
                        "token": token.string()
                    },
                    200)
            else:
                return (
                    {"message":"Username or password is invalid"},
                    "601 INVALID CREDENTIALS"
                )
        else:
            return (
                    {"message":"Username or password is invalid"},
                    "601 INVALID CREDENTIALS"
                )

class ChangePassword(Resource):
    '''
    Change the password.

    Expected JSON Data Format:
    ----------
    header = {
        "User-Agent":"XXXXX",
        "Authorization":"API_KEY XXXXXXXXXXXXXXXXXXXXXX"
    }
    data = {
        "username":"XXXXX",
        "current_password":"XXXXXXXXXXXXXXXXXXXXXX",
        "new_password":"XXXXXXXXXXXXXXXXXXXXXX",
        "confirm_password":"XXXXXXXXXXXXXXXXXXXXXX"
    }

    Returns:
    -----------
    If password changed successfully:
        status_code = 201
        data = {"message": "Successfully changed password for user 'XXXXX'"}
    Else if username does not exist:
        status_code = 604
        data = {"message": "Failed to change password"}
    Else if password is invalid:
        status_code = 604
        data = {"message": "Failed to change password"}
    Else if new password != confirm password:
        status_code = 604
        data = {"message": "Confirm password does not match the new password"}
    '''
    @required_api_auth
    def post(self):
        data = request.get_json()

        # Check username existence
        user = User.query.filter_by(username=data.get('username')).first()
        if user:
            is_pw_correct = check_password_hash(user.password_hash,
                                                data.get('current_password'))
            if is_pw_correct:
                # Check if new password == confirm password
                if data.get('new_password') == data.get('confirm_password'):
                    user.password_hash = generate_password_hash(
                        data.get('new_password'),
                        salt_length=16
                    )
                    db.session.commit()

                    return (
                        {"message": f"Successfully changed password for user '{user.username}'"},
                        200
                    )
                else:
                    return (
                        {"message": "Confirm password does not match the new password"},
                        "604 FAILED CHANGING PASSWORD"
                    )
            else:
                return (
                    {"message":"Failed to change password"},
                    "604 FAILED CHANGING PASSWORD"
                )
        else:
            return (
                    {"message":"Failed to change password"},
                    "604 FAILED CHANGING PASSWORD"
                )

class RegisterUser(Resource):
    '''
    Register a new user to the database.

    Expected JSON Data Format:
    ----------
    header = {
        "User-Agent":"XXXXX",
        "Authorization":"API_KEY XXXXXXXXXXXXXXXXXXXXXX"
    }
    data = {
        "username":"XXXXX",
        "email": "XXXXX@XXXmail.com",
        "password":"XXXXXXXXXXXXXXXXXXXXXX"
    }

    Returns:
    -----------
    If credentials correct:
        status_code = 201
        data = {"message": "Successfully created user 'XXXXX'"}
    Else if username exists:
        status_code = 602
        data = {"message": "Username is already used"}
    Else if email exists:
        status_code = 602
        data = {"message": "Email is already registered"}
    '''
    @required_api_auth
    def post(self):
        data = request.get_json()

        # Check username & email existence
        username_exist = User.query.filter_by(
            username=data.get('username')
        ).first()
        email_exist = User.query.filter_by(
            email=data.get('email')
        ).first()
        if username_exist:
            return (
                {"message":"Username is already used"},
                "602 UNSUCCESSFUL REGISTRATION"
            )
        elif email_exist:
            return (
                {"message":"Email is already registered"},
                "602 UNSUCCESSFUL REGISTRATION"
            )
        else:
            user = User(username=data.get('username'),
                        email=data.get('email'),
                        password_hash=generate_password_hash(
                            data.get('password'),
                            salt_length=16))
            db.session.add(user)
            db.session.commit()
            return (
                {
                    "message":
                    f"Successfully created user '{user.username}'"
                },
                201
            )

class GenerateAPIKey(Resource):
    '''
    This API can generate API Key and write to the relevant database.
    
    This is only allowed for learning purposes, we should avoid doing this 
    in actual case and try to exclude the generation of API Key out of the 
    application itself.

    Note: Admin API key required for this request.

    Expected JSON Data Format:
    ----------
    {
        "device_name": <device_name>
    }

    <device_name>: str (less than 50 characters)

    Returns:
    ----------
    If device name exists:
        status_code = 603
        data = {"message":"Device name is already used"}
    Else:
        status_code = 200
        data = {"api_key": "XXXXXXXXXXXXXXXXXXXXXX"}
    '''
    @required_admin_api_auth
    def post(self):
        data = request.get_json()

        # Check if device name is used
        device_exist = APIKey.query.filter_by(
                           device_name=data.get('device_name')).first()

        if device_exist:
            return (
                {"message":"Device name is already used"},
                "603 UNSUCCESSFUL KEYGEN"
            )
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
                return (
                    {"api_key":api_key},
                    200
                )

class ValidateToken(Resource):
    '''
    Validate the access token stored in the request's cookies.

    Returns:
    ----------
    status_code = 200
    data = {"is_token_valid": `Bool`}
    '''
    @required_api_auth
    def get(self):
        if request.cookies.get('token'):
            # print('validating token')
            token = Token(request.cookies['token'])
            # if token.validate(): print('token is valid')
            # else: print('token is invalid')
            return (
                {"is_token_valid":token.validate()},
                200
            )
        else:
            # print('token is invalid')
            return (
                {"is_token_valid":False},
                200
            )

class _TestApiAuth(Resource):
    '''
    For unit test purpose.
    Not for whatsoever production usage.
    '''
    @required_api_auth
    def get(self):
        return ({"message":"API successfully authorized"},200)

    @required_admin_api_auth
    def post(self):
        return ({"message":"Admin API successfully authorized"},200)

class _TestPlayGround(Resource):
    '''
    Playground API
    Not for whatsoever production usage.
    This API is solely for testing only.
    '''
    @required_api_auth
    def get(self):
        return ({"message":"success"},200)

    @required_admin_api_auth
    def post(self):
        return ({"message":"success"},200)



# Routing
api.add_resource(CheckPassword,'/checkpassword')
api.add_resource(ChangePassword,'/changepassword')
api.add_resource(RegisterUser,'/registeruser')
api.add_resource(GenerateAPIKey,'/generateapikey')
api.add_resource(ValidateToken,'/validatetoken')
api.add_resource(_TestPlayGround,'/testplayground')
api.add_resource(_TestApiAuth,'/testapiauth')
