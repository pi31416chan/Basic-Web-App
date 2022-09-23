# Imports
import hmac
from hashlib import sha256
from uuid import uuid4
from base64 import b64decode, b64encode,urlsafe_b64encode
from flask import (
    current_app,
    request
)
import json
from datetime import (
    datetime,
    timedelta
)
from secrets import token_hex,token_bytes



# Class Definition
class Token(dict):
    '''
    Pass in a token dictionary to instantiate a token object or generate
    it from scratch.

    If a token dictionary is passed in as argument, this is the
    expected format:
        token = {
            'user_agent': 'PostmanRuntime/7.29.2',
            'expiry': '2022-09-20T13:52:35.036640',
            'signature': 'abcdef123456abcdef123456abcdef123456'
        }
    '''
    def __init__(self,token_dict=None,user_agent=None,expiry=1800):
        # Check input
        if bool(token_dict) == bool(user_agent):
            raise AssertionError(
                'Please pass only either token_dict or ' +
                'user_agent as argument but not both.'
            )
        else:
            if token_dict is None:
                super().__init__(self._generate_token(expiry,user_agent))
            else:
                if isinstance(token_dict,str):
                    token_dict = b64decode(token_dict).decode('utf-8')
                    token_dict = json.loads(token_dict)
                super().__init__(token_dict)
                self.user_agent = token_dict['user_agent']
                self.expiry = token_dict['expiry']
                self.signature = token_dict['signature']

    @classmethod
    def _hash(cls,item):
        '''
        Hash any dictionary with HMAC algorithm
        '''
        _hmac_hash = hmac.new(
                bytes.fromhex(current_app.config['TOKEN_SECRET_KEY']),
                json.dumps(item).encode('utf-8'),
                sha256
            ).digest()
        
        return b64encode(_hmac_hash).decode('utf-8')
    
    def _validate_expiry(self):
        _expiry = datetime.fromisoformat(self.expiry)
        _cur_time = datetime.utcnow()
        # print(_expiry)
        # print(_cur_time)

        return _cur_time > _expiry

    def _validate_user_agent(self):
        _user_agent = request.user_agent.string
        # print(self.user_agent)
        # print(_user_agent)

        return self.user_agent == _user_agent

    @classmethod
    def _generate_token(cls,expiry,user_agent=None):
        '''
        Generate an expirable access token with HMAC algorithm.
        Expiry data is based on UTC time.

        Example:
        ----------
        token = {
            'user_agent': 'PostmanRuntime/7.29.2',
            'expiry': '2022-09-20T13:52:35.036640',
            'signature': 'abcdef123456abcdef123456abcdef123456'
        }
        '''
        cls.user_agent = user_agent
        cls.expiry = datetime.isoformat(
            datetime.utcnow() + timedelta(0,expiry)
        )
        _dict = {
            'user_agent': cls.user_agent,
            'expiry': cls.expiry
        }
        cls.signature = cls._hash(_dict)
        _dict.update({'signature':cls.signature})

        return cls(_dict)
    
    def validate(self):
        '''
        Validate the content of the token with its signature to detect
        token tampering.

        Returns: Bool
        '''
        if ('expiry' in self.keys() and 
            'signature' in self.keys()):
            _signature = self.pop('signature')
            
            # Check if the token is unmodified
            _sign_valid = hmac.compare_digest(
                _signature,
                self._hash(self)
            )
            if _sign_valid:
                # print('hash ok')
                self.update({'signature':_signature})
                
                # Check if the token is expired and user agent is correct
                _is_user_agent_correct = self._validate_user_agent()
                _is_expired = self._validate_expiry()
                # print(_is_user_agent_correct,_is_expired)
                if not _is_user_agent_correct or _is_expired:
                    # print('expired')
                    return False
                else:
                    # print('not expired')
                    return True
            else:
                # print('wrong hash')
                return False
        else:
            return False

    def string(self):
        return b64encode(json.dumps(self).encode('utf-8')).decode('utf-8')



# Function Definition
def generate_uuid_b64() -> str:
    '''
    Generate a random UUID with UUID version 4 and return as a base64 
    encoded string.
    '''
    id = uuid4()
    id_b64_b = urlsafe_b64encode(id.bytes)
    id_b64_str = id_b64_b.decode('ascii').replace('=','')
    return id_b64_str

def generate_random_key(type:str='hex',nbytes:int=32) -> str:
    '''
    Generate random 256 bit secret key.

    Parameters:
    ----------
    type: str, Default = 'hex'
        The type of the output key.
            'hex': generate a hexadecimal string
            'bytes': generate a hexadecimal string
    nbytes: int, Default = 32
        The byte size of the output key (32 bytes = 256 bits).

    Returns:
    ----------
    str or bytes
    '''
    if type == 'hex':
        return token_hex(nbytes)
    elif type == 'bytes':
        return token_bytes(nbytes)
    else:
        raise ValueError("Only 'hex' or 'bytes' are supported as argument")
        

def parse_auth_header(string:str) -> str:
    '''
    Takes a string from HTTP request's "Authorization" header, parse it and
    return as a plain api_key.

    Example:
    ----------
    request.headers = {"Authorization":"API_KEY N43Ffz1USOmCVpwKiVfMaQ"}

    >>> parse_auth_header(request.headers.get("Authorization"))
    N43Ffz1USOmCVpwKiVfMaQ
    '''
    # Check if string starts with "API_KEY "
    if string.startswith('API_KEY '):
        return string.replace('API_KEY ','')
    else:
        raise ValueError("Invalid api key")
