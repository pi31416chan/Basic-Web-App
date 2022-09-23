# Imports
import unittest
import os
from datetime import datetime as dt
from package.tests.test_misc import (
    suite_keygen,
    suite_uuid,
    suite_authparser
)
from package.tests.test_token import suite_token



# Function Definition
def log_result(resultlist,datetime):
    os.makedirs('./testlogs',exist_ok=True)

    f = open(f'./testlogs/test_{datetime}.log','a',encoding='utf-8')
    for testclass,string in resultlist:
        f.write(str(testclass)+'\n')
        f.write(string+'\n')
    
    return f.name



# Add Test Suite Here
suites_to_run = [
    suite_keygen,
    suite_uuid,
    suite_authparser,
    suite_token
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

    runner = unittest.TextTestRunner()

    print(f'Started Unit Test at {iso_datetime}')

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
        print('Unit Test Report')
        print('Features Tested:',len(successful))
        print('Features Failed:',len(unsuccessful))
        print('Tests Run:',testruns)
        print('Errors:',len(errors))
        print('Failures:',len(failures))
        print('Skipped:',len(skipped))
        if logged:
            print(f'Error, failure and skipped results saved to {path}')
        print('End of Unit Test Report')
