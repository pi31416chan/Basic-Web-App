# Imports
from flask import Flask
from datetime import datetime as dt, timedelta
from ..helper_func import (
    Token
)
from .base import (
    BaseTest,
    make_suite
)



# Variables
# This secret key is not used anywhere else and is solely for testing
# purpose
token_secret_key = "4391f4125f93796498876c0c583dccba0e51aad4e447ea0e0b013f1b4ea16855"



'''
Testing for Token Class
'''
class Test_CreateToken(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.app_context():
            self.token = Token(user_agent="Test User Agent",expiry=100000)
            self.keys = ['user_agent','expiry','signature']
            self.user_agent = self.token.get('user_agent')
            self.expiry = dt.fromisoformat(self.token.get('expiry'))
            self.signature = self.token.get('signature')
            self.apparent_expiry_a = dt.utcnow() + timedelta(0,99990)
            self.apparent_expiry_b = dt.utcnow() + timedelta(0,100010)

    def test_TokenDictKeys(self):
        is_keys_ok = (len([key in self.token.keys() for key in self.keys]) == 3)
        self.assertTrue(is_keys_ok)

    def test_TokenUserAgent(self):
        is_ua_ok = (self.user_agent == 'Test User Agent')
        self.assertTrue(is_ua_ok)

    def test_TokenDictKey(self):
        is_expiry_ok = ((self.expiry > self.apparent_expiry_a) and \
                        (self.expiry < self.apparent_expiry_b))
        self.assertTrue(is_expiry_ok)

    def test_TokenSignatureRegex(self):
        self.assertRegex(self.signature,'[0-9a-zA-Z+/=]{44}')

    def test_TokenSignatureLength(self):
        self.assertEqual(len(self.signature),44)

    def tearDown(self):
        del self.app

class Test_ReconstructTokenDict(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.app_context():
            self.token_dict = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
                'expiry': '2022-09-21T03:39:07.825274',
                'signature': 'IAfuNU+F03jScfDUDkDx+4bHB55ZnsEqrqr5haeyt/E='
            }
            self.token = Token(self.token_dict)

    def test_TokenAccuracy(self):
        self.assertEqual(dict(self.token),self.token_dict)

    def tearDown(self):
        del self.app

class Test_ReconstructTokenStr(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.app_context():
            self.token_str = \
                "eyJ1c2VyX2FnZW50IjogIlRlc3QgVXNlciBBZ2VudCIsICJleHBpcnkiOiA"+\
                "iMjAyMi0wOS0yMlQxNjoyODo1NS45MDM4ODEiLCAic2lnbmF0dXJlIjogIm"+\
                "tyZ2hmbmRzaGR3cFMxQkxyNXA4RnVyWVJwUkpNdy8zVyt0R0U3U1Y3cGM9In0="
            self.token_dict = {
                'user_agent': 'Test User Agent', 
                'expiry': '2022-09-22T16:28:55.903881', 
                'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='
            }
            self.token = Token(self.token_str)

    def test_TokenAccuracy(self):
        self.assertEqual(dict(self.token),self.token_dict)

    def tearDown(self):
        del self.app

class Test_TokenValidateSuccess(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.test_request_context(headers={"User-Agent":"Test User Agent"}):
            self.token = Token(user_agent="Test User Agent",expiry=3600)
            self.is_validate = self.token.validate()

    def test_TokenValidateSuccess(self):
            self.assertTrue(self.is_validate)

    def tearDown(self):
        del self.app

class Test_TokenValidateExpired(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.test_request_context(headers={"User-Agent":"Test User Agent"}):
            self.token = Token(user_agent="Test User Agent",expiry=-3600)
            self.is_validate = self.token.validate()

    def test_TokenValidateExpired(self):
            self.assertFalse(self.is_validate)

    def tearDown(self):
        del self.app

class Test_TokenValidateWrongUserAgent(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.test_request_context(headers={"User-Agent":"Lapsap User Agent"}):
            self.token = Token(user_agent="Test User Agent",expiry=3600)
            self.is_validate = self.token.validate()

    def test_TokenValidateWrongUserAgent(self):
            self.assertFalse(self.is_validate)

    def tearDown(self):
        del self.app

class Test_TokenValidateTampered(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.test_request_context(headers={"User-Agent":"Test User Agent"}):
            self.token = Token(user_agent="Test User Agent",expiry=-3600)
            self.token['expiry'] = str(dt.now() + timedelta(0,86400))
            self.is_validate = self.token.validate()

    def test_TokenValidateTampered(self):
            self.assertFalse(self.is_validate)

    def tearDown(self):
        del self.app

class Test_TokenPrintToken(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.app_context():
            self.token_dict = {
                'user_agent': 'Test User Agent', 
                'expiry': '2022-09-22T16:28:55.903881', 
                'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='
            }
            self.token = Token(self.token_dict)

    def test_TokenPrint(self):
        token_str = "{'user_agent': 'Test User Agent', "+\
                    "'expiry': '2022-09-22T16:28:55.903881', "+\
                    "'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='}"
        self.assertEqual(str(self.token),token_str)

    def tearDown(self):
        del self.app

class Test_TokenStringMethod(BaseTest):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TOKEN_SECRET_KEY'] = token_secret_key
        with self.app.app_context():
            self.token_dict = {
                'user_agent': 'Test User Agent',
                'expiry': '2022-09-22T16:28:55.903881',
                'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='
            }
            self.token = Token(self.token_dict)

    def test_TokenStringMethod(self):
        token_b64 = \
        "eyJ1c2VyX2FnZW50IjogIlRlc3QgVXNlciBBZ2VudCIsICJleHBpcnkiOiA"+\
        "iMjAyMi0wOS0yMlQxNjoyODo1NS45MDM4ODEiLCAic2lnbmF0dXJlIjogIm"+\
        "tyZ2hmbmRzaGR3cFMxQkxyNXA4RnVyWVJwUkpNdy8zVyt0R0U3U1Y3cGM9In0="
        self.assertEqual(self.token.string(),token_b64)

    def tearDown(self):
        del self.app

token_cases = [
    Test_CreateToken,Test_ReconstructTokenDict,Test_ReconstructTokenStr,
    Test_TokenValidateSuccess,Test_TokenValidateExpired,
    Test_TokenValidateWrongUserAgent,Test_TokenValidateTampered,
    Test_TokenPrintToken,Test_TokenStringMethod
]
suite_token = make_suite(
    token_cases,
    "Testing for Token Class"
)
