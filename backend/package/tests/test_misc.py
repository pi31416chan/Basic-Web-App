# Imports
from base64 import urlsafe_b64decode
from ..helper_func import (
    generate_random_key,
    generate_uuid_b64,
    parse_auth_header
)
from .base import (
    BaseTest,
    make_suite
)



'''
Testing for Random Key Generator
'''
class Test_KeyGenHexInput(BaseTest):
    def setUp(self):
        self.key = generate_random_key('hex',16)

    def test_KeyRegex(self):
        self.assertRegex(self.key,'[a-f0-9]{32}')

    def test_KeyLength(self):
        self.assertEqual(len(self.key),32)

class Test_KeyGenBytesInput(BaseTest):
    def setUp(self):
        self.key = generate_random_key('bytes',32)

    def test_KeyInstance(self):
        self.assertIsInstance(self.key,bytes)

    def test_KeyLength(self):
        self.assertEqual(len(self.key),32)

class Test_KeyGenWrongInput(BaseTest):
    def test_WrongInput(self):
        self.assertRaises(
            ValueError,
            lambda:generate_random_key('lapsap',16)
        )

keygen_cases = [
    Test_KeyGenHexInput,Test_KeyGenBytesInput,Test_KeyGenWrongInput
]
suite_keygen = make_suite(
    keygen_cases,
    "Testing for Random Key Generator"
)



'''
Testing for UUID Base64 Key Generator
'''
class Test_UUIDKey(BaseTest):
    def setUp(self):
        self.key = generate_uuid_b64()

    def test_Regex(self):
        self.assertRegex(self.key,'[a-zA-Z0-9\-\_]{22}')

    def test_Length(self):
        self.assertEqual(len(self.key),22)

class Test_UUIDHexKey(BaseTest):
    def setUp(self):
        self.key = generate_uuid_b64()
        self.key_hex = urlsafe_b64decode(self.key+"==").hex()

    def test_Regex(self):
        self.assertRegex(self.key_hex,'[a-f0-9]{32}')

    def test_Length(self):
        self.assertEqual(len(self.key_hex),32)

uuid_cases = [
    Test_UUIDKey,Test_UUIDHexKey
]
suite_uuid = make_suite(
    uuid_cases,
    "Testing for UUID Base64 Key Generator"
)



'''
Testing for Authorization Header Parser
'''
class Test_AuthParserValidInput(BaseTest):
    def setUp(self):
        # This key will and must not be used anywhere else and is solely
        # for testing purposes
        self.key = "API_KEY Jeml7ib-TwqinbDaV_GtlQ"
        self.parsed_key = parse_auth_header(self.key)

    def test_Regex(self):
        self.assertRegex(self.key,'[a-zA-Z0-9\-\_]{22}')

    def test_Match(self):
        self.assertEqual(self.parsed_key,"Jeml7ib-TwqinbDaV_GtlQ")

    def test_Length(self):
        self.assertEqual(len(self.parsed_key),22)

class Test_AuthParserWrongInput(BaseTest):
    def setUp(self):
        # This key will and must not be used anywhere else and is solely
        # for testing purposes
        self.key = "LAPSAP Jeml7ib-TwqinbDaV_GtlQ"

    def test_WrongInput(self):
        self.assertRaises(ValueError,lambda:parse_auth_header(self.key))

authparser_cases = [
    Test_AuthParserValidInput,Test_AuthParserWrongInput
]
suite_authparser = make_suite(
    authparser_cases,
    "Testing for Authorization Header Parser"
)
