from multiprocessing.sharedctypes import Value
import unittest
from base64 import urlsafe_b64decode
from ..helper_func import (
    generate_random_key,
    generate_uuid_b64,
    parse_auth_header
)
from .base import BaseTest



class TestKeyGen(BaseTest):        
    def test_hex_input(self):
        key = generate_random_key('hex',16)
        self.assertRegex(key,'[a-f0-9]*')
        self.assertEqual(len(key),32)

    def test_bytes_input(self):
        key = generate_random_key('bytes',32)
        self.assertIsInstance(key,bytes)
        self.assertEqual(len(key),32)

    def test_wrong_input(self):
        self.assertRaises(ValueError,lambda:generate_random_key('lapsap',16))

class TestUUIDGen(BaseTest):
    def test_uuid(self):
        key = generate_uuid_b64()
        key_hex = urlsafe_b64decode(key+"==").hex()
        self.assertRegex(key,'[a-zA-Z0-9-_]*')
        self.assertEqual(len(key),22)
        self.assertRegex(key_hex,'[a-f0-9]*')
        self.assertEqual(len(key_hex),32)

class TestAuthParser(BaseTest):
    def test_valid_arg(self):
        # This key will and must not be used anywhere else and is solely
        # for testing purposes
        key = "API_KEY Jeml7iboTwqinbDaVSGtlQ"
        parsed_key = parse_auth_header(key)
        with self.subTest('message 1'):
            self.assertEqual(parsed_key,"Jeml7iboTwqinbDaVSGtlQ")
        with self.subTest('message 2'):
            self.assertEqual(len(parsed_key),22)

    def test_invalid_arg(self):
        key = "LAPSAP Jeml7iboTwqinbDaVSGtlQ"
        self.assertRaises(ValueError,lambda:parse_auth_header(key))
