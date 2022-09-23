import unittest



class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('\n'+'----------'*7)
        print(f'Started {cls.__name__} ',end='',flush=True)

    @classmethod
    def tearDownClass(cls):
        print(f' Ended')
