# Imports
from base64 import (
    b64encode,
    b64decode
)
from flask import (
    Flask,
    current_app
)
from werkzeug.test import Client
import json
from datetime import (
    datetime as dt,
    timedelta
)
from ..helper_func import generate_uuid_b64
from ..db import (
    db
)
from ..api import (
    api
)
from .base import (
    APIBaseTest,
    make_suite
)



if __name__ == '__main__':
    # Initialization of flask app
    app = Flask(__name__)
    api.init_app(app)
    db.init_app(app)

    # Setting default config
    app.config['SECRET_KEY'] = \
        "cb94069919d5378563d41635e3abf8b8762e486e6e6880389d23264a699bb06f"
    app.config['TOKEN_SECRET_KEY'] = \
        "d84c3e65bf47376fa0b2f444bee5e377aa84504d0819eff95ab097082316695c"
    app.config['TOKEN_EXPIRY'] = 3600
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        "sqlite:///.../database/test.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    client = Client(app,use_cookies=False)
else:
    client = Client(current_app,use_cookies=False)



'''
Testing for /generateapikey API
'''
class Test_APIGenerateAPIKey(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY frcPOGw-RwSxQYtWShqrZQ"
        }
        self.payload = {
            "device_name":generate_uuid_b64(),
        }
        self.resp = client.post(
            '/generateapikey',
            headers=self.header,
            json=self.payload
        )
        self.resp_data = self.resp.get_json()

    def test_DBExistence(self):
        self._set_api_instance()
        self.assertTrue(self.api_instance)

    def test_KeyRegex(self):
        self._set_api_instance()
        self.assertRegex(self.resp_data['api_key'],'[a-zA-Z0-9\-\_]{22}')

    def test_KeyLength(self):
        self._set_api_instance()
        self.assertEqual(len(self.resp_data['api_key']),22)

    def test_DeviceNameAccuracy(self):
        self._set_api_instance()
        self.assertEqual(
            self.api_instance.device_name,
            self.payload['device_name']
        )

    def test_IsActive(self):
        self._set_api_instance()
        self.assertTrue(self.api_instance.active)

    def tearDown(self):
        if self.api_instance:
            db.session.delete(self.api_instance)
            db.session.commit()

apikeygen_cases = [
    Test_APIGenerateAPIKey
]
suite_apikeygen = make_suite(
    apikeygen_cases,
    "Testing for /generateapikey API"
)



'''
Testing for /registeruser API
'''
class Test_APIRegisterSuccess(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.payload = {
            "username":"test123",
            "email":"test123@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_user_from_db(self.payload['username'])
        self.resp = client.post(
            '/registeruser',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,201)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Successfully created user 'test123'"
        )

    def tearDown(self):
        self._clear_user_from_db(self.payload['username'])

class Test_APIRegisterUserExist(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.payload = {
            "username":"test123",
            "email":"test123@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_n_create_db(self.payload)
        self.payload['email'] = "test999@testmail.com"
        self.resp = client.post(
            '/registeruser',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,602)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Username is already used"
        )

    def tearDown(self):
        self._clear_user_from_db(self.payload['username'])

class Test_APIRegisterEmailExist(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.payload = {
            "username":"test123",
            "email":"test123@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_n_create_db(self.payload)
        self.old_username = self.payload['username']
        self.payload['username'] = "test999"
        self.resp = client.post(
            '/registeruser',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,602)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Email is already registered"
        )

    def tearDown(self):
        self._clear_user_from_db(self.old_username)

apiregisteruser_cases = [
    Test_APIRegisterSuccess,Test_APIRegisterUserExist,
    Test_APIRegisterEmailExist
]
suite_apiregisteruser = make_suite(
    apiregisteruser_cases,
    "Testing for /registeruser API"
)



'''
Testing for /checkpassword API
'''
class Test_CheckPasswordCorrect(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/checkpassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,201)

    def test_IsPasswordCorrect(self):
        self.assertTrue(self.resp.json['is_pw_correct'])

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Username and password correct"
        )

    def test_TokenRegex(self):
        length = len(self.resp.json['token'])
        pattern = '[0-9a-zA-Z+/=]{'+str(length)+'}'
        self.assertRegex(self.resp.json['token'],pattern)

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

class Test_CheckPasswordWrong(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456",
            "password":"123456789!@#$%^&*abcdefg?",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/checkpassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,601)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Username or password is invalid"
        )

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

class Test_CheckPasswordUserNotExist(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456?",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/checkpassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,601)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Username or password is invalid"
        )

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

apicheckpassword_cases = [
    Test_CheckPasswordCorrect,Test_CheckPasswordWrong,
    Test_CheckPasswordUserNotExist
]
suite_apicheckpassword = make_suite(
    apicheckpassword_cases,
    "Testing for /checkpassword API"
)



'''
Testing for /changepassword API
'''
class Test_ChangePasswordCorrect(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456",
            "current_password":"123456789!@#$%^&*abcdefg",
            "new_password":"987654321*&^%$#@!gfedcba",
            "confirm_password":"987654321*&^%$#@!gfedcba",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/changepassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,201)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            f"Successfully changed password for user '{self.user_payload['username']}'"
        )

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

class Test_ChangePasswordUserNotExist(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456?",
            "current_password":"123456789!@#$%^&*abcdefg",
            "new_password":"987654321*&^%$#@!gfedcba",
            "confirm_password":"987654321*&^%$#@!gfedcba",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/changepassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,604)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Failed to change password"
        )

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

class Test_ChangePasswordWrong(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456",
            "current_password":"123456789!@#$%^&*abcdefg?",
            "new_password":"987654321*&^%$#@!gfedcba",
            "confirm_password":"987654321*&^%$#@!gfedcba",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/changepassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,604)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Failed to change password"
        )

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

class Test_ChangePasswordUnmatched(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test456",
            "email":"test456@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test456",
            "current_password":"123456789!@#$%^&*abcdefg",
            "new_password":"987654321*&^%$#@!gfedcba",
            "confirm_password":"randomunmatchedpassword",
        }
        self._clear_n_create_db(self.user_payload)
        self.resp = client.post(
            '/changepassword',
            headers=self.header,
            json=self.payload
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,604)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Confirm password does not match the new password"
        )

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])

apichangepassword_cases = [
    Test_ChangePasswordCorrect,Test_ChangePasswordUserNotExist,
    Test_ChangePasswordWrong,Test_ChangePasswordUnmatched

]
suite_apichangepassword = make_suite(
    apichangepassword_cases,
    "Testing for /changepassword API"
)



'''
Testing for /validatetoken API
'''
class Test_ValidateTokenSuccess(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test789",
            "email":"test789@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test789",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_n_create_db(self.user_payload)
        self.token = client.post(
            '/checkpassword',
            headers=self.header,
            json=self.payload
        ).json['token']

        # Creating a client with cookies enabled
        self.client = Client(
            current_app,
            use_cookies=True
        )
        self.client.set_cookie(
            current_app.name,
            'token',
            self.token
        )
        self.resp = self.client.get(
            '/validatetoken',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_IsTokenValid(self):
        self.assertTrue(self.resp.json['is_token_valid'])

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])
        del self.client

class Test_ValidateTokenNoToken(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }

        # Creating a client with cookies enabled
        self.client = Client(
            current_app,
            use_cookies=True
        )
        self.client.set_cookie(
            current_app.name,
            'some',
            'other stuffs'
        )
        self.resp = self.client.get(
            '/validatetoken',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_IsTokenValid(self):
        self.assertFalse(self.resp.json['is_token_valid'])

    def tearDown(self):
        del self.client

class Test_ValidateTokenExpired(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.token = \
            "eyJ1c2VyX2FnZW50IjogIlRlc3QgVXNlciBBZ2VudCIsICJleHBpcnkiOiAi"+\
            "MjAyMi0wOS0yNFQwNzoyODowMi4wNTM3NzUiLCAic2lnbmF0dXJlIjogInhB"+\
            "bUtYSjIvVDdycWhkc2Jma0hUQzN3bkxlbU5Oand1NTduQ005RlJ0MTA9In0="

        # Creating a client with cookies enabled
        self.client = Client(
            current_app,
            use_cookies=True
        )
        self.client.set_cookie(
            current_app.name,
            'token',
            self.token
        )
        self.resp = self.client.get(
            '/validatetoken',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_IsTokenValid(self):
        self.assertFalse(self.resp.json['is_token_valid'])

    def tearDown(self):
        del self.client

class Test_ValidateTokenWrongUserAgent(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.user_payload = {
            "username":"test789",
            "email":"test789@testmail.com",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self.payload = {
            "username":"test789",
            "password":"123456789!@#$%^&*abcdefg",
        }
        self._clear_n_create_db(self.user_payload)
        self.token = client.post(
            '/checkpassword',
            headers=self.header,
            json=self.payload
        ).json['token']

        # Creating a client with cookies enabled
        self.client = Client(
            current_app,
            use_cookies=True
        )
        self.client.set_cookie(
            current_app.name,
            'token',
            self.token
        )
        self.fakeheader = {
            "User-Agent":"Lapsap User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.resp = self.client.get(
            '/validatetoken',
            headers=self.fakeheader
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_IsTokenValid(self):
        self.assertFalse(self.resp.json['is_token_valid'])

    def tearDown(self):
        self._clear_user_from_db(self.user_payload['username'])
        del self.client

class Test_ValidateTokenTampered(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.token = \
            "eyJ1c2VyX2FnZW50IjogIlRlc3QgVXNlciBBZ2VudCIsICJleHBpcnkiOiAi"+\
            "MjAyMi0wOS0yNFQwNzoyODowMi4wNTM3NzUiLCAic2lnbmF0dXJlIjogInhB"+\
            "bUtYSjIvVDdycWhkc2Jma0hUQzN3bkxlbU5Oand1NTduQ005RlJ0MTA9In0="
        self.token = json.loads(b64decode(self.token).decode('utf-8'))
        self.token['expiry'] = dt.isoformat(
            dt.fromisoformat(self.token['expiry']) +\
            timedelta(3650)
        )
        self.token = b64encode(
            json.dumps(self.token).encode('utf-8')
        ).decode('utf-8')

        # Creating a client with cookies enabled
        self.client = Client(
            current_app,
            use_cookies=True
        )
        self.client.set_cookie(
            current_app.name,
            'token',
            self.token
        )
        self.resp = self.client.get(
            '/validatetoken',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_IsTokenValid(self):
        self.assertFalse(self.resp.json['is_token_valid'])

    def tearDown(self):
        del self.client

apivalidatetoken_cases = [
    Test_ValidateTokenSuccess,Test_ValidateTokenNoToken,
    Test_ValidateTokenExpired,Test_ValidateTokenWrongUserAgent,
    Test_ValidateTokenTampered
]
suite_apivalidatetoken = make_suite(
    apivalidatetoken_cases,
    "Testing for /validatetoken API"
)



'''
Testing for /testapiauth API
'''
class Test_APIAuthSuccess(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.resp = client.get(
            '/testapiauth',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "API successfully authorized"
        )

class Test_APIAuthNoKey(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
        }
        self.resp = client.get(
            '/testapiauth',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,401)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Authorized api key is required for this request"
        )

class Test_APIAuthWrongKey(Test_APIAuthNoKey):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY AAAAAAAAAAAAAAAAAAAAAA"
        }
        self.resp = client.get(
            '/testapiauth',
            headers=self.header
        )

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Api key is invalid"
        )

class Test_APIAuthWrongKeyFormat(Test_APIAuthWrongKey):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"AAAAAAAAAAAAAAAAAAAAAA"
        }
        self.resp = client.get(
            '/testapiauth',
            headers=self.header
        )

apitestapiauth_cases = [
    Test_APIAuthSuccess,Test_APIAuthNoKey,
    Test_APIAuthWrongKey,Test_APIAuthWrongKeyFormat
]
suite_apitestapiauth = make_suite(
    apitestapiauth_cases,
    "Testing for /validatetoken API"
)



'''
Testing for /testapiauth Admin Only API
'''
class Test_APIAdminAuthSuccess(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY frcPOGw-RwSxQYtWShqrZQ"
        }
        self.resp = client.post(
            '/testapiauth',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,200)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Admin API successfully authorized"
        )

class Test_APIAdminAuthNoKey(APIBaseTest):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
        }
        self.resp = client.post(
            '/testapiauth',
            headers=self.header
        )

    def test_Status(self):
        self.assertEqual(self.resp.status_code,401)

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Authorized api key is required for this request"
        )

class Test_APIAdminAuthClientValidKey(Test_APIAdminAuthNoKey):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY TJhf6diDRxCDVBLKZi3sTA"
        }
        self.resp = client.post(
            '/testapiauth',
            headers=self.header
        )

    def test_Message(self):
        self.assertEqual(
            self.resp.json['message'],
            "Api key is invalid"
        )

class Test_APIAdminAuthWrongKey(Test_APIAdminAuthClientValidKey):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"API_KEY AAAAAAAAAAAAAAAAAAAAAA"
        }
        self.resp = client.post(
            '/testapiauth',
            headers=self.header
        )

class Test_APIAdminAuthWrongKeyFormat(Test_APIAdminAuthClientValidKey):
    def setUp(self):
        self.header = {
            "User-Agent":"Test User Agent",
            "Authorization":"AAAAAAAAAAAAAAAAAAAAAA"
        }
        self.resp = client.post(
            '/testapiauth',
            headers=self.header
        )

apiadmintestapiauth_cases = [
    Test_APIAdminAuthSuccess,Test_APIAdminAuthNoKey,
    Test_APIAdminAuthClientValidKey,Test_APIAdminAuthWrongKey,
    Test_APIAdminAuthWrongKeyFormat
]
suite_apiadmintestapiauth = make_suite(
    apiadmintestapiauth_cases,
    "Testing for /testapiauth Admin Only API"
)
