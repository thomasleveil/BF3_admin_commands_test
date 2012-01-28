import sys, os
import unittest
import logging
from protocol import FrostbiteServer, CommandFailedError

__all__ = ['Bf3_test_config', 'load_config_file', 'expect_error', 'BF3_connected_TestCase', 'BF3_authenticated_TestCase', 'CommandFailedError']


class Bf3_test_config(object):
    host = None
    port = None
    pw = None
    skip_time_consuming_tests = None
    ranked = None


def load_config_file():
    # load BF3 test server info from config.ini file
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')

    def print_help_config_file():
        print """ERROR: cannot find config file '%s'

    config file content should look like :

            [BF3]
            host = xx.xx.xx.xx
            port = 47000
            password = s3cr3t

            [TESTS]
            skip_time_consuming_tests = true

        """ % config_file


    if not os.path.isfile(config_file):
        print_help_config_file()
        sys.exit(1)

    import ConfigParser
    try:
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        Bf3_test_config.host = config.get('BF3', 'host')
        Bf3_test_config.port = config.getint('BF3', 'port')
        Bf3_test_config.pw = config.get('BF3', 'password')
        Bf3_test_config.ranked = config.getboolean('BF3', 'ranked')
        Bf3_test_config.skip_time_consuming_tests = config.getboolean('TESTS', 'skip_time_consuming_tests')
    except ConfigParser.NoSectionError, err:
        print "ERROR: %r" % err
        print_help_config_file()
        sys.exit(1)



class expect_error(object):
    """
    decorator to expect CommandFailedError while sending a command to the BF3 server.
    """

    def __init__(self, error_type=''):
        self.error_type = error_type

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except CommandFailedError, err:
                if err.message[0] != self.error_type:
                    raise AssertionError("expecting %s, got %r instead" % (self.error_type, err))
            else:
                raise AssertionError("expecting error %s" % self.error_type)
        return wrapper




class TestFailuresTypes(tuple):
    """
    class that acts a a tuple but when called acts as if AssertionError was called.

    Setting a unittest.TestCase failureException attribute to an instance of TestFailuresTypes can make the test runner
    interpret additional exception types as failures instead of errors.
    """
    def __call__(self, *args, **kwargs):
        return AssertionError(*args, **kwargs)



class _BF3_TestCase(object):

    protocol_log_level = logging.ERROR

    @classmethod
    def setUpClassCommon(cls):
        if Bf3_test_config.host is None or Bf3_test_config.port is None:
            raise AssertionError("BF3 test server host and port not set")

        FORMAT = "%(name)-20s [%(thread)-4d] %(threadName)-15s %(levelname)-8s %(message)s"
        formatter = logging.Formatter(FORMAT)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logging.getLogger('FrostbiteServer').addHandler(handler)
        logging.getLogger('FrostbiteServer').setLevel(cls.protocol_log_level)

        logging.getLogger('FrostbiteDispatcher').addHandler(handler)
        logging.getLogger('FrostbiteDispatcher').setLevel(logging.ERROR)




class BF3_connected_TestCase(unittest.TestCase):

    failureException = TestFailuresTypes((AssertionError, CommandFailedError))
    t_conn = None

    @classmethod
    def setUpClass(cls):
        """
        Setup loggers, connect to the test BF3 server.
        Run once for the whole class.
        """
        super(BF3_connected_TestCase, cls).setUpClassCommon()

        try:
            cls.t_conn = FrostbiteServer(Bf3_test_config.host, Bf3_test_config.port)
        except:
            if hasattr(cls, 't_conn') and cls.t_conn:
                cls.t_conn.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        """
        run once after all tests are done.
        """
        cls.t_conn.stop()


    def cmd(self, *args):
        """
        convenient shortcut to send a command from our test methods.
        """
        return self.__class__.t_conn.command(*args)

BF3_connected_TestCase.__bases__ += (_BF3_TestCase, )





class BF3_authenticated_TestCase(unittest.TestCase):

    failureException = TestFailuresTypes((AssertionError, CommandFailedError))
    t_conn = None

    @classmethod
    def setUpClass(cls):
        """
        Setup loggers, connect and auth to the test BF3 server.
        Run once for the whole class.
        """
        super(BF3_authenticated_TestCase, cls).setUpClassCommon()

        try:
            cls.t_conn = FrostbiteServer(Bf3_test_config.host, Bf3_test_config.port, Bf3_test_config.pw)
            cls.t_conn.auth()
        except:
            if hasattr(cls, 't_conn') and cls.t_conn:
                cls.t_conn.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        """
        run once after all tests are done.
        """
        cls.t_conn.stop()


    def cmd(self, *args):
        """
        convenient shortcut to send a command from our test methods.
        """
        return self.__class__.t_conn.command(*args)

BF3_authenticated_TestCase.__bases__ += (_BF3_TestCase, )
