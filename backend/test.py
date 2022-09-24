# Imports
import unittest
import os
from datetime import datetime as dt
from flask import Flask
from package import (
    api,
    db
)
from package.tests.test_misc import (
    suite_keygen,
    suite_uuid,
    suite_authparser,
)
from package.tests.test_token import suite_token
from package.tests.test_api import (
    suite_apikeygen,
    suite_apiregisteruser,
    suite_apicheckpassword,
    suite_apivalidatetoken,
    suite_apitestapiauth,
    suite_apiadmintestapiauth
)



# Function Definition
def log_result(resultlist,datetime):
    os.makedirs('./testlogs',exist_ok=True)

    f = open(f'./testlogs/test_{datetime}.log','a',encoding='utf-8')
    for testclass,string in resultlist:
        f.write(str(testclass)+'\n')
        f.write(string+'\n')
    
    return f.name




app = Flask(__name__)
app.config['SECRET_KEY'] = \
    "cb94069919d5378563d41635e3abf8b8762e486e6e6880389d23264a699bb06f"
app.config['TOKEN_SECRET_KEY'] = \
    "d84c3e65bf47376fa0b2f444bee5e377aa84504d0819eff95ab097082316695c"
app.config['TOKEN_EXPIRY'] = 3600
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "sqlite:///./database/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api.init_app(app)
db.init_app(app)
with app.app_context():
    db.create_all()



# Add Test Suite Here
suites_to_run = [
    suite_keygen,
    suite_uuid,
    suite_authparser,
    suite_token,
    suite_apikeygen,
    suite_apiregisteruser,
    suite_apicheckpassword,
    suite_apivalidatetoken,
    suite_apitestapiauth,
    suite_apiadmintestapiauth
]



# Main
if __name__ == '__main__':
    successful = []
    unsuccessful = []
    testruns = 0
    errors = []
    failures = []
    skipped = []
    logged = False
    iso_datetime = dt.isoformat(dt.now(),timespec='seconds')
    f_datetime = dt.now().strftime('%Y%m%d_%H-%M-%S')

    with app.test_request_context():
        runner = unittest.TextTestRunner()

        print(f'<<< Started Unit Test at {iso_datetime} >>>')

        for suite in suites_to_run:
            result = suite(runner)

            if result.wasSuccessful():
                successful.append(result.wasSuccessful())
            else:
                unsuccessful.append(result.wasSuccessful())
            if len(result.errors) > 0:
                errors += result.errors
            if len(result.failures) > 0:
                failures += result.failures
            if len(result.skipped) > 0:
                skipped += result.skipped
            testruns += result.testsRun
        else:
            if errors:
                path = log_result(errors,f_datetime)
                logged = True
            if failures:
                path = log_result(failures,f_datetime)
                logged = True
            if skipped:
                path = log_result(skipped,f_datetime)
                logged = True

            print('\n'+'----------'*7)
            print('<<< Unit Test Report Sumamry >>>')
            print('Features Tested:',len(successful))
            print('Features Failed:',len(unsuccessful))
            print('Tests Run:',testruns)
            print('Errors:',len(errors))
            print('Failures:',len(failures))
            print('Skipped:',len(skipped))
            if logged:
                print(f'Error, failure and skipped results saved to {path}')
            print('<<< End of Unit Test Report >>>')
