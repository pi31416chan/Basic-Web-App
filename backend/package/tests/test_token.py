import unittest
import os
import sys
from flask import Flask
from datetime import datetime as dt, timedelta
from ..helper_func import (
    Token,
    generate_random_key,
    generate_uuid_b64,
    parse_auth_header
)



# Test Case
class TestToken(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        # This secret key is not used anywhere else and is solely for testing 
        # purpose
        self.app.config['TOKEN_SECRET_KEY'] = "4391f4125f93796498876c0c583dccba0e51aad4e447ea0e0b013f1b4ea16855"

    def tearDown(self):
        del self.app

    def test_create_token(self):
        with self.app.app_context():
            token = Token(user_agent="Test User Agent",expiry=100000)
            keys = ['user_agent','expiry','signature']
            apparent_expiry_a = dt.utcnow() + timedelta(0,99990)
            apparent_expiry_b = dt.utcnow() + timedelta(0,100010)


            is_keys_ok = (sum([key in token.keys() for key in keys]) == 3)
            is_ua_ok = (token.get('user_agent') == 'Test User Agent')
            is_expiry_ok = ((dt.fromisoformat(token.get('expiry')) > apparent_expiry_a) and \
                            (dt.fromisoformat(token.get('expiry')) < apparent_expiry_b))

            self.assertTrue(is_keys_ok)
            self.assertTrue(is_ua_ok)
            self.assertTrue(is_expiry_ok)

    def test_reconstruct_token_dict(self):
        with self.app.app_context():
            token_dict = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
                'expiry': '2022-09-21T03:39:07.825274',
                'signature': 'IAfuNU+F03jScfDUDkDx+4bHB55ZnsEqrqr5haeyt/E='
            }
            self.assertEqual(dict(Token(token_dict)),token_dict)

    def test_reconstruct_token_str(self):
        with self.app.app_context():
            token_str = \
                "eyJ1c2VyX2FnZW50IjogIlRlc3QgVXNlciBBZ2VudCIsICJleHBpcnkiOiA"+\
                "iMjAyMi0wOS0yMlQxNjoyODo1NS45MDM4ODEiLCAic2lnbmF0dXJlIjogIm"+\
                "tyZ2hmbmRzaGR3cFMxQkxyNXA4RnVyWVJwUkpNdy8zVyt0R0U3U1Y3cGM9In0="
            token_dict = {
                'user_agent': 'Test User Agent', 
                'expiry': '2022-09-22T16:28:55.903881', 
                'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='
            }
            self.assertEqual(dict(Token(token_str)),token_dict)

    def test_validate_valid(self):
        with self.app.test_request_context(headers={"User-Agent":"Test User Agent"}):
            token = Token(user_agent="Test User Agent",expiry=3600)
            self.assertTrue(token.validate())

    def test_validate_expired(self):
        with self.app.test_request_context(headers={"User-Agent":"Test User Agent"}):
            token = Token(user_agent="Test User Agent",expiry=-3600)
            self.assertFalse(token.validate())

    def test_validate_wrong_useragent(self):
        with self.app.test_request_context(headers={"User-Agent":"Lapsap User Agent"}):
            token = Token(user_agent="Test User Agent",expiry=3600)
            self.assertFalse(token.validate())

    def test_validate_tampered(self):
        with self.app.test_request_context(headers={"User-Agent":"Test User Agent"}):
            token = Token(user_agent="Test User Agent",expiry=-3600)
            token['expiry'] = str(dt.now() + timedelta(0,86400))
            self.assertFalse(token.validate())

    def test_print_token(self):
        with self.app.app_context():
            token_dict = {
                'user_agent': 'Test User Agent', 
                'expiry': '2022-09-22T16:28:55.903881', 
                'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='
            }
            token = Token(token_dict)
            self.assertEqual(str(token),
            "{'user_agent': 'Test User Agent', "+
            "'expiry': '2022-09-22T16:28:55.903881', "+
            "'signature': 'krghfndshdwpS1BLr5p8FurYRpRJMw/3W+tGE7SV7pc='}")
            self.assertEqual(token.string(),
            "eyJ1c2VyX2FnZW50IjogIlRlc3QgVXNlciBBZ2VudCIsICJleHBpcnkiOiA"+
            "iMjAyMi0wOS0yMlQxNjoyODo1NS45MDM4ODEiLCAic2lnbmF0dXJlIjogIm"+
            "tyZ2hmbmRzaGR3cFMxQkxyNXA4RnVyWVJwUkpNdy8zVyt0R0U3U1Y3cGM9In0=")



if __name__ == '__main__':
    unittest.main()