# Imports
import unittest
from werkzeug.security import generate_password_hash
from ..db import (
    APIKey,
    User,
    db
)



#Class Definition
class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(f'Started {cls.__name__} ',end='',flush=True)

    @classmethod
    def tearDownClass(cls):
        print(f' Ended')



# Class Definition
class APIBaseTest(BaseTest):
    def _clear_user_from_db(self,username):
        exist_user = User.query.filter_by(
            username=username
        ).first()
        if exist_user:
            db.session.delete(exist_user)
            db.session.commit()

    def _create_user_to_db(self,payload):
        user = User(
            username=payload['username'],
            email=payload['email'],
            password_hash=generate_password_hash(
                payload['password'],
                salt_length=16
            )
        )
        db.session.add(user)
        db.session.commit()

    def _clear_n_create_db(self,payload):
        self._clear_user_from_db(payload['username'])
        self._create_user_to_db(payload)

    def _set_api_instance(self):
        self.api_instance = APIKey.query.filter_by(
            key=self.resp_data['api_key']
        ).first()



# Function Definition
def make_suite(testlist,header):

    def suite_func(runner):
        testsuites = [unittest.makeSuite(test) for test in testlist]
        suite = unittest.TestSuite()
        suite.addTests(testsuites)

        print('\n'+'----------'*7)
        print(f'Started {header}\n')
        result = runner.run(suite)
        print(f'Ended')

        return result

    return suite_func
