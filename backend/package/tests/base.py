# Imports
import unittest



#Class Definition
class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(f'Started {cls.__name__} ',end='',flush=True)

    @classmethod
    def tearDownClass(cls):
        print(f' Ended')



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
