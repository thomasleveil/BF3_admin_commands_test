# -*- encoding: utf-8 -*-
if __name__ == '__main__':
    import unittest, os

    loader = unittest.TestLoader()
    tests = loader.discover(start_dir=os.path.join(os.path.dirname(__file__), 'test_R19'))

    testRunner = unittest.TextTestRunner(verbosity=2)
    testRunner.run(tests)
