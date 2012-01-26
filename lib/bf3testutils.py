import unittest
import logging
from protocol import FrostbiteServer, CommandFailedError



class expect_error(object):
    """
    decorator to expect CommandFailedError while sending a command to the BF3 server.
    """

    def __init__(self, error_type=''):
        self.error_type = error_type

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except CommandFailedError, err:
                if err.message[0] != self.error_type:
                    raise AssertionError("expecting %s, got %r instead" % (self.error_type, err))
            else:
                raise AssertionError("expecting %s, got success instead : %r" % (self.error_type, res))
        return wrapper




class _BF3_TestCase(object):

    protocol_log_level = logging.ERROR
    bf3_host = None
    bf3_port = None
    bf3_passwd = None

    @classmethod
    def setUpClassCommon(cls):
        if cls.bf3_host is None or cls.bf3_port is None:
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

    t_conn = None

    @classmethod
    def setUpClass(cls):
        """
        Setup loggers, connect to the test BF3 server.
        Run once for the whole class.
        """
        super(BF3_connected_TestCase, cls).setUpClassCommon()

        try:
            cls.t_conn = FrostbiteServer(cls.bf3_host, cls.bf3_port)
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

    t_conn = None

    @classmethod
    def setUpClass(cls):
        """
        Setup loggers, connect and auth to the test BF3 server.
        Run once for the whole class.
        """
        if cls.bf3_passwd is None:
            raise AssertionError("BF3 test server password not set")

        super(BF3_authenticated_TestCase, cls).setUpClassCommon()

        try:
            cls.t_conn = FrostbiteServer(cls.bf3_host, cls.bf3_port, cls.bf3_passwd)
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
