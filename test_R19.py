# -*- encoding: utf-8 -*-
import os, sys, re, Queue, logging, threading, time
import unittest
from lib.bf3testutils import expect_error, BF3_authenticated_TestCase, BF3_connected_TestCase
from lib.protocol import CommandFailedError, CommandTimeoutError, generatePasswordHash


# load BF3 test server info from config.ini file
config_file = os.path.join(os.path.dirname(__file__), 'config.ini')

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
    host = config.get('BF3', 'host')
    port = config.getint('BF3', 'port')
    pw = config.get('BF3', 'password')
    skip_time_consuming_tests = config.getboolean('TESTS', 'skip_time_consuming_tests')
except ConfigParser.NoSectionError, err:
    print_help_config_file()
    sys.exit(1)


print "Test running against BF3 server %s:%s" % (host, port)


R19_version = '903227'


class Test_admin_eventsEnabled(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.eventsEnabled [enabled: boolean]

    def test_nominal_no_arg(self):
        self.assertIn(self.cmd('admin.eventsEnabled'), (['true'], ['false']))

    def test_nominal_true_false(self):
        self.cmd('admin.eventsEnabled', 'true')
        self.assertEqual(['true'], self.cmd('admin.eventsEnabled'))
        self.cmd('admin.eventsEnabled', 'false')
        self.assertEqual(['false'], self.cmd('admin.eventsEnabled'))
        self.cmd('admin.eventsEnabled', 'true')
        self.assertEqual(['true'], self.cmd('admin.eventsEnabled'))

    @expect_error('InvalidArguments')
    def test_bad_argument(self):
        self.cmd('admin.eventsEnabled', 'f00')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('admin.eventsEnabled', 'true', 'false')



class Test_admin_password(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.password [password: password]

    def test_nominal_no_argument(self):
        self.assertEqual([pw], self.cmd('admin.password'))

    @unittest.skip("this one will set an empty string as password. Is this what the doc means by 'reset' the password ?")
    def test_empty_string_argument(self):
        self.cmd('admin.password', '')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('admin.password', 'sdf', 'f00')

    @expect_error('InvalidPassword')
    def test_password_with_forbidden_chars(self):
        self.cmd('admin.password', '%ù*_-(){}')



class Test_admin_help(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.help

    def test_nominal(self):
        all_commands = set(['admin.eventsEnabled', 'admin.help', 'admin.kickPlayer', 'admin.killPlayer', 'admin.listPlayers',
            'admin.movePlayer', 'admin.password', 'admin.say', 'admin.shutDown', 'banList.add', 'banList.clear',
            'banList.list', 'banList.load', 'banList.remove', 'banList.save', 'currentLevel', 'gameAdmin.add',
            'gameAdmin.clear', 'gameAdmin.list', 'gameAdmin.load', 'gameAdmin.remove', 'gameAdmin.save', 'listPlayers',
            'login.hashed', 'login.plainText', 'logout', 'mapList.add' ,'mapList.availableMaps', 'mapList.clear',
            'mapList.endRound', 'mapList.getMapIndices', 'mapList.getRounds', 'mapList.list', 'mapList.load',
            'mapList.remove', 'mapList.restartRound', 'mapList.runNextRound', 'mapList.save', 'mapList.setNextMapIndex',
            'punkBuster.activate', 'punkBuster.isActive', 'punkBuster.pb_sv_command', 'quit',
            'reservedSlotsList.add', 'reservedSlotsList.clear', 'reservedSlotsList.list', 'reservedSlotsList.load',
            'reservedSlotsList.remove', 'reservedSlotsList.save', 'serverInfo', 'unlockList.add', 'unlockList.clear',
            'unlockList.list', 'unlockList.remove', 'unlockList.save', 'vars.3dSpotting', 'vars.3pCam', 'vars.autoBalance',
            'vars.bannerUrl', 'vars.bulletDamage', 'vars.friendlyFire', 'vars.gameModeCounter', 'vars.gamePassword',
            'vars.hud', 'vars.idleBanRounds', 'vars.idleTimeout', 'vars.killCam', 'vars.killRotation', 'vars.maxPlayers',
            'vars.minimap', 'vars.miniMapSpotting', 'vars.nameTag', 'vars.onlySquadLeaderSpawn', 'vars.playerManDownTime',
            'vars.playerRespawnTime', 'vars.ranked', 'vars.regenerateHealth', 'vars.roundRestartPlayerCount', 'vars.roundsPerMap',
            'vars.roundStartPlayerCount', 'vars.serverDescription', 'vars.serverMessage', 'vars.serverName', 'vars.soldierHealth',
            'vars.teamKillCountForKick', 'vars.teamKillKickForBan', 'vars.teamKillValueDecreasePerSecond', 'vars.teamKillValueForKick',
            'vars.teamKillValueIncrease', 'vars.unlockMode', 'vars.vehicleSpawnAllowed', 'vars.vehicleSpawnDelay', 'version',
        ])
        result = self.cmd('admin.help')
        self.assertEqual(all_commands, set(result))

    @expect_error('InvalidArguments')
    def test_bad_argument(self):
        self.cmd('admin.help', 'f00')



class Test_serverInfo(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## serverInfo

    def test_nominal(self):
        self.cmd('serverInfo')

    @expect_error('InvalidArguments')
    def test_with_junk(self):
        self.cmd('serverInfo', 'f00')




class Test_admin_kickPlayer(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.kickPlayer <soldier name: player name> [reason: string]

    @expect_error('PlayerNotFound')
    def test_non_existing_player(self):
        self.cmd('admin.kickPlayer', 'f00')

    @expect_error('PlayerNotFound')
    def test_non_existing_player_with_reason(self):
        self.cmd('admin.kickPlayer', 'f00', 'reason')

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('admin.kickPlayer')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('admin.kickPlayer', 'playername', 'reason', 'f00')



class Test_admin_movePlayer(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.movePlayer <name: player name> <teamId: Team ID> <squadId: Squad ID> <forceKill: boolean>

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('admin.movePlayer')

    @expect_error('InvalidArguments')
    def test_one_argument(self):
        self.cmd('admin.movePlayer', 'name')

    @expect_error('InvalidArguments')
    def test_two_arguments(self):
        self.cmd('admin.movePlayer', 'name', '0')

    @expect_error('InvalidArguments')
    def test_three_arguments(self):
        self.cmd('admin.movePlayer', 'name', '0', '0')

    @expect_error('InvalidPlayerName')
    def test_non_existing_player(self):
        self.cmd('admin.movePlayer', 'f00', '0', '0', 'false')



class Test_admin_killPlayer(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.killPlayer <name: player name>

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('admin.killPlayer')

    @expect_error('InvalidPlayerName')
    def test_non_existing_player(self):
        self.cmd('admin.killPlayer', 'f00')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('admin.killPlayer', 'name', 'f00')



class Test_punkBuster(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw


    ## punkBuster.isActive

    def test_punkBuster_isActive__nominal(self):
        self.assertIn(self.cmd('punkBuster.isActive'), (['true'], ['false']))



    ## punkBuster.activate

    def test_punkBuster_activate__nominal(self):
        self.cmd('punkBuster.activate')



    ## punkBuster.pb_sv_command <command: string>

    def test_punkBuster_pb_sv_command__nominal_PB_SV_List(self):
        self.cmd('punkBuster.pb_sv_command', 'PB_SV_List')

    @expect_error('InvalidPbServerCommand')
    def test_punkBuster_pb_sv_command__bad_pb_command(self):
        self.cmd('punkBuster.pb_sv_command', 'f00')

    @expect_error('InvalidArguments')
    def test_punkBuster_pb_sv_command__no_arg(self):
        self.cmd('punkBuster.pb_sv_command')




class Test_admin_listPlayers(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.listPlayers


    def test_all_nominal(self):
        res = self.cmd('admin.listPlayers', 'all')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_team_nominal(self):
        res = self.cmd('admin.listPlayers', 'team', '0')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_squad_nominal(self):
        res = self.cmd('admin.listPlayers', 'squad', '0', '0')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_player_nominal(self):
        res = self.cmd('admin.listPlayers', 'player', 'f00')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', '0'], res)



    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('admin.listPlayers')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('admin.listPlayers', 'f00', 'f00', 'f00', 'f00')

    @expect_error('InvalidArguments')
    def test_bad_argument(self):
        self.cmd('admin.listPlayers', 'f00')

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('admin.listPlayers')

    @expect_error('InvalidArguments')
    def test_all_and_junk(self):
        self.cmd('admin.listPlayers', 'all', 'f00')

    @expect_error('InvalidArguments')
    def test_team_no_team_number(self):
        self.cmd('admin.listPlayers', 'team')

    @expect_error('InvalidArguments')
    def test_team_and_junk(self):
        self.cmd('admin.listPlayers', 'team', 'f00')

    @expect_error('InvalidArguments')
    def test_squad_no_team_number(self):
        self.cmd('admin.listPlayers', 'squad')

    @expect_error('InvalidArguments')
    def test_squad_and_junk(self):
        self.cmd('admin.listPlayers', 'squad', 'f00')

    @expect_error('InvalidArguments')
    def test_squad_no_squad_number(self):
        self.cmd('admin.listPlayers', 'squad', '0')

    @expect_error('InvalidArguments')
    def test_squad_too_many_arguments(self):
        self.cmd('admin.listPlayers', 'squad', '0', '0', '0', '0')

    @expect_error('InvalidArguments')
    def test_player_and_no_player_name(self):
        self.cmd('admin.listPlayers', 'player')

    @expect_error('InvalidArguments')
    def test_player_too_many_arguments(self):
        self.cmd('admin.listPlayers', 'player', 'f00', 'fOO')




class Test_admin_say(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    ## admin.say <message: string> <players: player subset>

    def test_nominal_all(self):
        self.cmd('admin.say', 'msg blah', 'all')

    def test_nominal_team(self):
        self.cmd('admin.say', 'msg blah', 'team', '0')

    def test_nominal_squad(self):
        self.cmd('admin.say', 'msg blah', 'squad', '0', '0')

    def test_nominal_player(self):
        self.cmd('admin.say', 'msg blah', 'player', 'f00')


    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('admin.say')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('admin.say', 'f00', 'f00', 'f00', 'f00', 'f00')

    @expect_error('InvalidArguments')
    def test_not_enough_argument(self):
        self.cmd('admin.say', 'f00')

    @expect_error('InvalidArguments')
    def test_all_and_junk(self):
        self.cmd('admin.say', 'msg blah', 'all', 'f00')

    @expect_error('InvalidTeam')
    def test_team_no_team_number(self):
        self.cmd('admin.say', 'msg blah', 'team')

    @expect_error('InvalidTeam')
    def test_team_and_junk(self):
        self.cmd('admin.say', 'msg blah', 'team', 'f00')

    @expect_error('InvalidSquad')
    def test_squad_no_team_number(self):
        self.cmd('admin.say', 'msg blah', 'squad')

    @expect_error('InvalidSquad')
    def test_squad_and_junk(self):
        self.cmd('admin.say', 'msg blah', 'squad', 'f00')

    @expect_error('InvalidSquad')
    def test_squad_no_squad_number(self):
        self.cmd('admin.say', 'msg blah', 'squad', '0')

    @expect_error('InvalidSquad')
    def test_squad_too_many_arguments(self):
        self.cmd('admin.say', 'msg blah', 'squad', '0', '0', '0', '0')

    @expect_error('InvalidPlayer')
    def test_player_and_no_player_name(self):
        self.cmd('admin.say', 'msg blah', 'player')

    @expect_error('InvalidPlayer')
    def test_player_too_many_arguments(self):
        self.cmd('admin.say', 'msg blah', 'player', 'f00', 'fOO')

    def test_nominal_128_char_message(self):
        # maximum message length is 128
        msg = '123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 12345678'
        self.assertEqual(128, len(msg))
        self.cmd('admin.say', msg, 'all')

    @expect_error('TooLongMessage')
    def test_129_char_message(self):
        # maximum message length is 128
        msg = '123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789'
        self.assertEqual(129, len(msg))
        self.cmd('admin.say', msg, 'all')




class _banList_TestCase(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    def _seek_number_of_bans(self):
        """
        fast computation of how many bans are in the banlist.
        Needed because no command provides the total number of bans.
        """

        def num_bans(data=[]):
            # each ban is composed of 6 word
            return len(data) / 6

        # check if empty or less than 100
        tmp_count = num_bans(self.cmd('banList.list'))
        if tmp_count < 100:
            return tmp_count

        # check if close to 10000
        tmp_count = num_bans(self.cmd('banList.list', '9901'))
        if tmp_count > 0:
            number_of_bans = 9901 + tmp_count
            print "current number of bans : %s <" % number_of_bans
            return number_of_bans

        # need to find out
        number_of_bans = None
        lower_bound = 0
        upper_bound = 10100
        previous_current = None
        current = (upper_bound - lower_bound) // 2
        while True:
            assert previous_current != current
            assert lower_bound <= current <= upper_bound,  "%5d < %5d < %5d" % (lower_bound, current, upper_bound)
            tmp_count = num_bans(self.cmd('banList.list', current))
            #print "[%5d (%3d)----- %5d ----- %5d]" % (lower_bound, tmp_count, current, upper_bound)
            if tmp_count == 0:
                upper_bound = current
                if lower_bound == upper_bound:
                    lower_bound -= 1
                current = lower_bound + ((upper_bound - lower_bound) // 2)
            elif tmp_count == 1:
                number_of_bans = current + 1
                break
            elif 1 < tmp_count < 100:
                lower_bound = current = current + tmp_count - 1
                if lower_bound >= upper_bound:
                    # this happens if bans are added while counting
                    upper_bound = lower_bound + 150
            else:
                lower_bound = current + 100
                current = lower_bound + ((upper_bound - lower_bound) // 2)
        print "current number of bans : %s" % number_of_bans
        return number_of_bans


    def _fill_10000_bans(self):
        """
        Use threads to fill up to 10000 bans faster.
        """
        class BanAdderThread(threading.Thread):
            lock = threading.Lock()
            count = None
            cmd = None

            def __init__(self, prefix=''):
                threading.Thread.__init__(self)
                self.prefix = prefix

            def run(self):
                while True:
                    with BanAdderThread.lock:
                        if BanAdderThread.count <= 0:
                            break
                        else:
                            BanAdderThread.count -= 1
                    try:
                        BanAdderThread.cmd('banList.add', 'name', '%s-%s' % (self.prefix, BanAdderThread.count), 'perm')
                    except CommandTimeoutError:
                        with BanAdderThread.lock:
                            BanAdderThread.count += 1

        BanAdderThread.cmd = self.cmd

        # seek how many bans are in the banlist
        num_bans = self._seek_number_of_bans()
        BanAdderThread.count = 10000 - num_bans

        if num_bans == 10000:
            return
        elif num_bans > 10000:
            self.fail("banList contains more than 10000 entries")


        if BanAdderThread.count > 50:
            # old_logging_level = logging.getLogger('FrostbiteServer').level
            # logging.getLogger('FrostbiteServer').setLevel(logging.INFO)

            # spawn threads
            threads = []
            for i in range(40):
                t = BanAdderThread(prefix='%s_%s' % (int(time.time()), i))
                threads.append(t)
                t.start()

            # wait for threads to end
            for t in threads:
                t.join()

            #logging.getLogger('FrostbiteServer').setLevel(old_logging_level)

            # we should have close to 10000 entries now, check again
            num_bans = self._seek_number_of_bans()

        consecutive_fails = 0
        while num_bans < 10000:
            try:
                self.cmd('banList.add', 'name', '%s-%s' % (int(time.time()), num_bans), 'perm')
                consecutive_fails = 0
                num_bans += 1
            except CommandTimeoutError:
                consecutive_fails += 1
                if consecutive_fails > 20:
                    self.fail("Too many timeouts when trying to fill 10000 bans")



class Test_banList_add(_banList_TestCase):

    ## banList.add <id-type, id, timeout, reason>

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('banList.add')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('banList.clear')
        self.cmd('banList.add', 'name', 'id', 'perm', 'reason', 'f00', 'bar')
        self.fail("expected error InvalidArguments, but command succeeded instead and banlist content is %r" % self.cmd('banList.list'))

    def test_reason_80_char(self):
        reason = 'reason 89 123456789 123456789 123456789 123456789 123456789 123456789 123456789 '
        self.assertEqual(80, len(reason))
        self.cmd('banList.clear')
        self.cmd('banList.add', 'name', 'id', 'perm', reason)
        self.assertEqual(['name', 'id', 'perm', '0', '0', reason], self.cmd('banList.list'))

    @expect_error('InvalidBanReason')
    def test_reason_81_char(self):
        reason = 'reason 89 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1'
        self.assertEqual(81, len(reason))
        self.cmd('banList.clear')
        self.cmd('banList.add', 'name', 'id', 'perm', reason)
        self.fail("expected error InvalidArguments, but command succeeded instead and banlist content is %r" % self.cmd('banList.list'))

    def _test_nominal(self, test_data):
        for args, expected in test_data:
            print "banList.add %s" % ", ".join(args)
            self.cmd('banList.clear')
            self.cmd('banList.add', *args)
            result = self.cmd('banList.list')
            try:
                self.assertEqual(expected[0:3], result[0:3])
                self.assertAlmostEqual(int(expected[3]), int(result[3]), delta=2)
                self.assertEqual(expected[4:], result[4:])
            except AssertionError:
                self.assertEqual(expected, result) # will give a better failure message with complete diff

    def test_nominal_by_name(self):
        self._test_nominal([
            (('name', 'f00', 'perm'),                       ['name', 'f00', 'perm', '0', '0', 'Banned by admin']),
            (('name', 'f00', 'perm', 'a reason'),           ['name', 'f00', 'perm', '0', '0', 'a reason']),
            (('name', 'f00', 'rounds', '1'),                ['name', 'f00', 'rounds', '0', '1', 'Banned by admin']),
            (('name', 'f00', 'rounds', '1', 'a reason'),    ['name', 'f00', 'rounds', '0', '1', 'a reason']),
            (('name', 'f00', 'seconds', '70'),              ['name', 'f00', 'seconds', '70', '0', 'Banned by admin']),
            (('name', 'f00', 'seconds', '150', 'a reason'), ['name', 'f00', 'seconds', '150', '0', 'a reason']),
        ])

    def test_nominal_by_ip(self):
        self._test_nominal([
            (('ip', '11.22.33.44', 'perm'),                       ['ip', '11.22.33.44', 'perm', '0', '0', 'Banned by admin']),
            (('ip', '11.22.33.44', 'perm', 'a reason'),           ['ip', '11.22.33.44', 'perm', '0', '0', 'a reason']),
            (('ip', '11.22.33.44', 'rounds', '1'),                ['ip', '11.22.33.44', 'rounds', '0', '1', 'Banned by admin']),
            (('ip', '11.22.33.44', 'rounds', '1', 'a reason'),    ['ip', '11.22.33.44', 'rounds', '0', '1', 'a reason']),
            (('ip', '11.22.33.44', 'seconds', '70'),              ['ip', '11.22.33.44', 'seconds', '70', '0', 'Banned by admin']),
            (('ip', '11.22.33.44', 'seconds', '150', 'a reason'), ['ip', '11.22.33.44', 'seconds', '150', '0', 'a reason']),
        ])

    def test_nominal_by_guid(self):
        self._test_nominal([
            (('guid', 'EA_00000000', 'perm'),                       ['guid', 'EA_00000000', 'perm', '0', '0', 'Banned by admin']),
            (('guid', 'EA_00000000', 'perm', 'a reason'),           ['guid', 'EA_00000000', 'perm', '0', '0', 'a reason']),
            (('guid', 'EA_00000000', 'rounds', '1'),                ['guid', 'EA_00000000', 'rounds', '0', '1', 'Banned by admin']),
            (('guid', 'EA_00000000', 'rounds', '1', 'a reason'),    ['guid', 'EA_00000000', 'rounds', '0', '1', 'a reason']),
            (('guid', 'EA_00000000', 'seconds', '70'),              ['guid', 'EA_00000000', 'seconds', '70', '0', 'Banned by admin']),
            (('guid', 'EA_00000000', 'seconds', '150', 'a reason'), ['guid', 'EA_00000000', 'seconds', '150', '0', 'a reason']),
        ])


    @unittest.skipIf(skip_time_consuming_tests and False, 'skipping time consuming test')
    def test_Full(self):
        # banList can contain up to 10000
        self._fill_10000_bans()
        self.assertEqual(10000, self._seek_number_of_bans())
        #self.cmd('banList.save')

        # verify that adding a 10001th map fails
        try:
            self.cmd('banList.add', 'ip', '11.33.22.44', 'perm')
            self.fail('expecting Full error')
        except CommandFailedError, err:
            self.assertEqual(['Full'], err.message, "expecting Full error but got %r" % err.message)





class Test_banList_remove(_banList_TestCase):

    ## banList.remove <id-type: id-type> <id: string>

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('banList.remove')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('banList.remove', 'f00', 'bar', 'blah')

    @expect_error('NotFound')
    def test_not_banned(self):
        self.cmd('banList.clear')
        self.cmd('banList.remove', 'name', 'f00')

    def test_nominal_by_name(self):
        self.cmd('banList.clear')
        self.cmd('banList.add', 'name', 'f00bar', 'perm')
        self.assertNotEqual([], self.cmd('banList.list'))
        self.cmd('banList.remove', 'name', 'f00bar')
        ban_list = self.cmd('banList.list')
        self.assertEqual([], ban_list, "expecting empty banlist, got %r" % ban_list)

    def test_nominal_by_ip(self):
        self.cmd('banList.clear')
        self.cmd('banList.add', 'ip', '11.44.55.22', 'perm')
        self.assertNotEqual([], self.cmd('banList.list'))
        self.cmd('banList.remove', 'ip', '11.44.55.22')
        ban_list = self.cmd('banList.list')
        self.assertEqual([], ban_list, "expecting empty banlist, got %r" % ban_list)

    def test_nominal_by_guid(self):
        self.cmd('banList.clear')
        self.cmd('banList.add', 'guid', 'EA_xxxxxxxx', 'perm')
        self.assertNotEqual([], self.cmd('banList.list'))
        self.cmd('banList.remove', 'guid', 'EA_xxxxxxxx')
        ban_list = self.cmd('banList.list')
        self.assertEqual([], ban_list, "expecting empty banlist, got %r" % ban_list)




class Test_banList_clear(_banList_TestCase):

    ## banList.clear

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('banList.clear', 'f00')

    def test_nominal(self):
        self.cmd('banList.add', 'name', 'f00bar', 'perm')
        self.assertNotEqual([], self.cmd('banList.list'))
        self.cmd('banList.clear')
        ban_list = self.cmd('banList.list')
        self.assertEqual([], ban_list, "expecting empty banlist, got %r" % ban_list)




class Test_banList_list(_banList_TestCase):

    ## banList.list [startIndex]

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('banList.list', '0', 'f00')

    @expect_error('InvalidArguments')
    def test_negative_index(self):
        self.cmd('banList.list', '-2')

    @expect_error('InvalidArguments')
    def test_bad_index(self):
        self.cmd('banList.list', 'f00')

    def test_nominal(self):
        self.cmd('banList.clear')
        self.cmd('banList.add', 'name', 'f001', 'perm')
        self.cmd('banList.add', 'name', 'f002', 'perm')
        self.cmd('banList.add', 'name', 'f003', 'perm')
        self.assertEqual(['name', 'f001', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f002', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f003', 'perm', '0', '0', 'Banned by admin'], self.cmd('banList.list'))
        self.assertEqual(['name', 'f001', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f002', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f003', 'perm', '0', '0', 'Banned by admin'], self.cmd('banList.list', '0'))
        self.assertEqual(['name', 'f002', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f003', 'perm', '0', '0', 'Banned by admin'], self.cmd('banList.list', '1'))
        self.assertEqual(['name', 'f003', 'perm', '0', '0', 'Banned by admin'], self.cmd('banList.list', '2'))
        self.assertEqual([], self.cmd('banList.list', '3'))




class Test_banList_load_save(_banList_TestCase):

    ## banList.load
    ## banList.save

    def test_nominal(self):
        self.cmd('banList.clear')
        self.cmd('banList.add', 'name', 'f001', 'perm')
        self.cmd('banList.add', 'name', 'f002', 'perm')
        self.cmd('banList.add', 'name', 'f003', 'perm')
        # save
        self.cmd('banList.save')
        self.cmd('banList.clear')
        self.assertEqual([], self.cmd('banList.list'))
        # load
        self.cmd('banList.load')
        self.assertEqual(['name', 'f001', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f002', 'perm', '0', '0', 'Banned by admin',
                          'name', 'f003', 'perm', '0', '0', 'Banned by admin'], self.cmd('banList.list'))

    @expect_error('InvalidArguments')
    def test_load__to_many_arguments(self):
        self.cmd('banList.load', 'f00')

    @expect_error('InvalidArguments')
    def test_save__to_many_arguments(self):
        self.cmd('banList.save', 'f00')





class Test_mapList(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    @classmethod
    def add_maps(cls, list_of_maps):
        """
        Fill the BF3 mapList with list_of_maps.

        list_of_maps is a list of (map name, game type, num round)
        """
        cls.t_conn.command('mapList.clear')
        for map_info in list_of_maps:
            cls.t_conn.command('mapList.add', map_info[0], map_info[1], map_info[2])


    ## mapList.clear

    def test_mapList_clear__nominal(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1')
        self.assertEqual(['1', '3', 'MP_001', 'RushLarge0', '1'], self.cmd('mapList.list'))
        self.cmd('mapList.clear')
        self.assertEqual(['0', '3'], self.cmd('mapList.list'))

    @expect_error('InvalidArguments')
    def test_mapList_clear__bad_argument(self):
        self.cmd('mapList.clear', 'junk')




    ## mapList.add

    def test_mapList_add__nominal(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1')
        self.assertEqual(['1', '3', 'MP_001', 'RushLarge0', '1'], self.cmd('mapList.list'))

    @expect_error('InvalidArguments')
    def test_mapList_add__missing_rounds_argument(self):
        self.cmd('mapList.add', 'MP_001', 'RushLarge0')

    @expect_error('InvalidArguments')
    def test_mapList_add__missing_rounds_and_game_type_arguments(self):
        self.cmd('mapList.add', 'MP_001')

    @expect_error('InvalidArguments')
    def test_mapList_add__no_argument(self):
        self.cmd('mapList.add')

    @expect_error('InvalidMap')
    def test_mapList_add__bad_map_argument(self):
        self.cmd('mapList.add', 'f00', 'RushLarge0', '1')

    @expect_error('InvalidGameModeOnMap')
    def test_mapList_add__InvalidGameModeOnMap(self):
        self.cmd('mapList.add', 'MP_001', 'f00', '1')

    @expect_error('InvalidRoundsPerMap')
    def test_mapList_add__0_round(self):
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '0')

    @expect_error('InvalidRoundsPerMap')
    def test_mapList_add__negative_number_of_rounds(self):
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '-1')

    @expect_error('InvalidRoundsPerMap')
    def test_mapList_add__too_many_rounds(self):
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1000000000000000')

    def test_mapList_add__highest_number_of_rounds_accepted(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1999999999999999')
        self.assertEqual(['1', '3', 'MP_001', 'RushLarge0', '1999999999999999'], self.cmd('mapList.list'))

    @unittest.skipIf(skip_time_consuming_tests, 'skipping time consuming test')
    def test_mapList_add__Full(self):
        self.cmd('mapList.clear')

        def add_20_maps():
            for i in range(20):
                try:
                    self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1')
                except CommandTimeoutError:
                    pass

        # add 200 maps to the mapList
        threads = []
        for i in range(10):
            t = threading.Thread(target=add_20_maps)
            threads.append(t)
            t.start()

        # wait for threads to end
        for t in threads:
            t.join()

        # make sure we have 200 maps in the list
        while int(self.cmd('mapList.list', '199')[0]) < 1:
            self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1')

        # verify that adding a 201th map fails
        try:
            self.cmd('mapList.add', 'MP_001', 'RushLarge0', '3')
            self.fail("expecting error Full")
        except CommandFailedError, err:
            self.assertEqual(['Full'], err.message, "expecting error Full, but got %r" % err.message)


    ## mapList.add with index

    def test_mapList_add_with_index__nominal(self):
        self.cmd('mapList.clear')
        # inserting at index 0
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', '0')
        self.assertEqual(['1', '3', 'MP_001', 'RushLarge0', '1'], self.cmd('mapList.list'))
        self.cmd('mapList.add', 'MP_003', 'ConquestSmall0', '2', '0')
        self.assertEqual(['2','3', 'MP_003','ConquestSmall0','2', 'MP_001','RushLarge0','1'], self.cmd('mapList.list'))
        self.cmd('mapList.add', 'MP_007', 'SquadRush0', '3', '0')
        self.assertEqual(['3','3', 'MP_007','SquadRush0','3', 'MP_003','ConquestSmall0','2', 'MP_001','RushLarge0','1'], self.cmd('mapList.list'))
        # inserting at index 2
        self.cmd('mapList.add', 'MP_013', 'TeamDeathMatch0', '4', '2')
        self.assertEqual(['4','3', 'MP_007','SquadRush0','3', 'MP_003','ConquestSmall0','2',  'MP_013','TeamDeathMatch0','4', 'MP_001','RushLarge0','1'], self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_add_with_index__index_1_on_empty_list(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', '1')
        self.fail("expecting InvalidMapIndex error, but command succeeded : %r" % self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_add_with_index__index_2_on_empty_list(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', '2')
        self.fail("expecting InvalidMapIndex error, but command succeeded : %r" % self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_add_with_index__empty_index(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', '')
        self.fail("expecting InvalidMapIndex error, but command succeeded : %r" % self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_add_with_index__negative_index(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', '-4')
        self.fail("expecting InvalidMapIndex error, but command succeeded : %r" % self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_add_with_index__bad_index(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', 'f00')
        self.fail("expecting InvalidMapIndex error, but command succeeded : %r" % self.cmd('mapList.list'))

    @expect_error('InvalidArguments')
    def test_mapList_add_with_index__too_many_arguments(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1', '5', 'f00', 'bar')
        self.fail("expecting InvalidArguments error, but command succeeded : %r" % self.cmd('mapList.list'))




    ## mapList.remove

    def test_mapList_remove__nominal(self):
        self.__class__.add_maps([
            ('MP_001', 'RushLarge0', '1'),
            ('MP_003', 'ConquestSmall0', '2'),
            ('MP_007', 'SquadDeathMatch0', '3'),
        ])
        self.assertEqual(['3','3',
                          'MP_001', 'RushLarge0', '1',
                          'MP_003', 'ConquestSmall0', '2',
                          'MP_007', 'SquadDeathMatch0', '3'],
            self.cmd('mapList.list'))
        self.cmd('mapList.remove', '1')
        self.assertEqual(['2','3',
                          'MP_001', 'RushLarge0', '1',
                          'MP_007', 'SquadDeathMatch0', '3'],
            self.cmd('mapList.list'))

    @expect_error('InvalidArguments')
    def test_mapList_remove__no_argument(self):
        self.cmd('mapList.remove')

    @expect_error('InvalidArguments')
    def test_mapList_remove__too_many_arguments(self):
        self.__class__.add_maps([('MP_001', 'RushLarge0', '1'), ('MP_003', 'ConquestSmall0', '2')])
        self.cmd('mapList.remove', '0', '0')
        self.assertEqual(['2','3', 'MP_001','RushLarge0','1', 'MP_003','ConquestSmall0','2'], self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_remove__on_an_empty_list(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.remove', '0')
        self.assertEqual(['0','3'], self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_remove__bad_index(self):
        self.__class__.add_maps([('MP_001', 'RushLarge0', '1'), ('MP_003', 'ConquestSmall0', '2')])
        self.cmd('mapList.remove', 'f00')
        self.assertEqual(['2','3', 'MP_001','RushLarge0','1', 'MP_003','ConquestSmall0','2'], self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_remove__negative_index(self):
        self.__class__.add_maps([('MP_001', 'RushLarge0', '1'), ('MP_003', 'ConquestSmall0', '2')])
        self.cmd('mapList.remove', '-1')
        self.assertEqual(['2','3', 'MP_001','RushLarge0','1', 'MP_003','ConquestSmall0','2'], self.cmd('mapList.list'))

    @expect_error('InvalidMapIndex')
    def test_mapList_remove__index_too_high(self):
        self.__class__.add_maps([('MP_001', 'RushLarge0', '1'), ('MP_003', 'ConquestSmall0', '2')])
        self.cmd('mapList.remove', '2')
        self.assertEqual(['2','3', 'MP_001','RushLarge0','1', 'MP_003','ConquestSmall0','2'], self.cmd('mapList.list'))



    ## mapList.list


    @expect_error('InvalidArguments')
    def test_mapList_list__too_many_arguments(self):
        self.cmd('mapList.list', '0', 'f00')

    def test_mapList_list__nominal(self):
        self.cmd('mapList.clear')
        self.assertEqual(['0', '3'], self.cmd('mapList.list'))
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1')
        self.assertEqual(['1', '3', 'MP_001', 'RushLarge0', '1'], self.cmd('mapList.list'))




    ## mapList.list with index

    def test_mapList_list_with_index__nominal(self):
        self.cmd('mapList.clear')
        self.assertEqual(['0', '3'], self.cmd('mapList.list', '0'))
        self.assertEqual(['0', '3'], self.cmd('mapList.list', '1'))
        self.assertEqual(['0', '3'], self.cmd('mapList.list', '50'))
        self.cmd('mapList.add', 'MP_001', 'RushLarge0', '1')
        self.cmd('mapList.add', 'MP_003', 'RushLarge0', '2')
        self.cmd('mapList.add', 'MP_007', 'RushLarge0', '3')
        self.cmd('mapList.add', 'MP_011', 'RushLarge0', '4')
        self.assertEqual(['4', '3', 'MP_001','RushLarge0','1', 'MP_003','RushLarge0','2',
                          'MP_007','RushLarge0','3', 'MP_011','RushLarge0','4'], self.cmd('mapList.list', '0'))
        self.assertEqual(['2', '3', 'MP_007','RushLarge0','3', 'MP_011','RushLarge0','4'], self.cmd('mapList.list', '2'))
        self.assertEqual(['0', '3'], self.cmd('mapList.list', '4'))


    @expect_error('InvalidArguments')
    def test_mapList_list_with_index__negative(self):
        self.cmd('mapList.list', '-1')

    @expect_error('InvalidArguments')
    def test_mapList_list_with_index__f00(self):
        self.cmd('mapList.list', 'f00')




    ## mapList.save and load roundtrip

    def test_mapList_save_load_nominal(self):
        self.__class__.add_maps([
            ('MP_001', 'RushLarge0', '1'),
            ('MP_003', 'ConquestSmall0', '2'),
            ('MP_007', 'SquadDeathMatch0', '3'),
        ])
        self.assertEqual(['3','3',
                          'MP_001', 'RushLarge0', '1',
                          'MP_003', 'ConquestSmall0', '2',
                          'MP_007', 'SquadDeathMatch0', '3'],
            self.cmd('mapList.list'))
        self.cmd('mapList.save')
        self.cmd('mapList.clear')
        self.assertEqual(['0','3'], self.cmd('mapList.list'))
        self.cmd('mapList.load')
        self.assertEqual(['3','3',
                          'MP_001', 'RushLarge0', '1',
                          'MP_003', 'ConquestSmall0', '2',
                          'MP_007', 'SquadDeathMatch0', '3'],
            self.cmd('mapList.list'))




    ## mapList.setNextMapIndex <index: integer>

    @expect_error('InvalidArguments')
    def test_mapList_setNextMapIndex__no_argument(self):
        self.cmd('mapList.setNextMapIndex')

    @expect_error('InvalidArguments')
    def test_mapList_setNextMapIndex__too_many_arguments(self):
        self.cmd('mapList.setNextMapIndex', '0', 'f00')

    @expect_error('InvalidMapIndex')
    def test_mapList_setNextMapIndex__negative_index(self):
        self.cmd('mapList.setNextMapIndex', '-5')

    @expect_error('InvalidMapIndex')
    def test_mapList_setNextMapIndex__too_high_index(self):
        self.cmd('mapList.clear')
        self.cmd('mapList.setNextMapIndex', '5')

    def test_mapList_setNextMapIndex__nominal(self):
        self.__class__.add_maps([
            ('MP_001', 'RushLarge0', '1'),
            ('MP_003', 'ConquestSmall0', '2'),
            ('MP_007', 'SquadDeathMatch0', '3'),
        ])
        self.cmd('mapList.setNextMapIndex', '0')
        self.cmd('mapList.setNextMapIndex', '1')
        self.cmd('mapList.setNextMapIndex', '2')



    ## mapList.getMapIndices

    @expect_error('InvalidArguments')
    def test_mapList_getMapIndices__too_many_arguments(self):
        self.cmd('mapList.getMapIndices', 'f00')

    def test_mapList_getMapIndices__empty_list(self):
        self.cmd('mapList.clear')
        res = self.cmd('mapList.getMapIndices')
        self.assertEqual(['0', '0'], res)

    def test_mapList_getMapIndices__one_map(self):
        self.__class__.add_maps([('MP_001', 'RushLarge0', '1')])
        res = self.cmd('mapList.getMapIndices')
        self.assertEqual(['0', '0'], res)




    ## mapList.getRounds

    def test_mapList_getRounds__nominal(self):
        server_info = self.cmd('serverInfo')
        self.assertEqual(server_info[5:7], self.cmd('mapList.getRounds'))

    @expect_error('InvalidArguments')
    def test_mapList_getRounds__too_many_arguments(self):
        self.cmd('mapList.getRounds', 'f00')




    ## mapList.runNextRound

    @expect_error('InvalidArguments')
    def test_mapList_runNextRound__too_many_arguments(self):
        self.cmd('mapList.runNextRound', 'f00')

    def test_mapList_runNextRound__nominal(self):
        self.cmd('mapList.runNextRound')



    ## mapList.restartRound

    @expect_error('InvalidArguments')
    def test_mapList_restartRound__too_many_arguments(self):
        self.cmd('mapList.restartRound', 'f00')

    def test_mapList_restartRound__nominal(self):
        self.cmd('mapList.restartRound')




    ## mapList.endRound <winner: Team ID>

    @expect_error('InvalidArguments')
    def test_mapList_endRound__no_argument(self):
        self.cmd('mapList.endRound')

    @expect_error('InvalidArguments')
    def test_mapList_endRound__too_many_arguments(self):
        self.cmd('mapList.endRound', '0', 'f00')

    @expect_error('InvalidArguments')
    def test_mapList_endRound__bad_team_id(self):
        self.cmd('mapList.endRound', 'f00')

    def test_mapList_endRound__nominal(self):
        self.cmd('mapList.endRound', '0')



    ## mapList.availableMaps

    @unittest.skip('mapList.availableMaps is said to be broken in documentation')
    def test_mapList_availableMaps(self):
        pass






@unittest.skip('todo Test_variables')
class Test_variables(BF3_authenticated_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port
    bf3_passwd = pw

    def test_Variables(self): pass






class Test_not_authenticated(BF3_connected_TestCase):

    protocol_log_level = logging.ERROR
    bf3_host = host
    bf3_port = port

    @expect_error('UnknownCommand')
    def test_unknown_command(self):
        self.cmd('f00')

    def test_login_plainText__and__logout__nominal(self):
        # verify that we are not logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] != 'LogInRequired':
                self.fail('expecting to be logged out')

        # try to authenticate
        res = self.cmd('login.plainText', pw)

        # verify that we are logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] == 'LogInRequired':
                self.fail('expecting to be logged in')
        # log out
        self.cmd('logout')
        # verify that we are not logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] != 'LogInRequired':
                self.fail('expecting to be logged out')



    def test_login_hashed__and__logout__nominal(self):
        # verify that we are not logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] != 'LogInRequired':
                self.fail('expecting to be logged out')

        # try to authenticate
        res = self.cmd('login.hashed')
        salt_string = res[0]
        self.assertEqual(32, len(salt_string), "expecting salt, got %r" % salt_string)
        self.assertIsNotNone(re.match('^[0-9A-F]{32}$', salt_string), "expecting 32 hexdigit salt, got %r" % salt_string)
        salt =salt_string.decode("hex")
        passwordHash = generatePasswordHash(salt, pw)
        passwordHashHexString = passwordHash.encode("hex").upper()
        self.cmd('login.hashed', passwordHashHexString)

        # verify that we are logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] == 'LogInRequired':
                self.fail('expecting to be logged in')
                # log out
        self.cmd('logout')
        # verify that we are not logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] != 'LogInRequired':
                self.fail('expecting to be logged out')



    @expect_error('InvalidArguments')
    def test_login_plainText__no_argument(self):
        self.cmd('login.plainText')

    @expect_error('InvalidArguments')
    def test_login_plainText__too_many_arguments(self):
        self.cmd('login.plainText', pw, 'f00')

    @expect_error('InvalidPassword')
    def test_login_plainText__bad_password(self):
        self.cmd('login.plainText', 'f00')



    def test_login_hashed__no_argument(self):
        res = self.cmd('login.hashed')
        salt = res[0]
        self.assertEqual(32, len(salt), "expecting salt, got %r" % salt)
        self.assertIsNotNone(re.match('^[0-9A-F]{32}$', salt), "expecting 32 hexdigit salt, got %r" % salt)


    @expect_error('InvalidPasswordHash')
    def test_login_hashed__bad_password(self):
        self.cmd('login.hashed')
        self.cmd('login.hashed', 'f00')

    @expect_error('InvalidArguments')
    def test_login_hashed__too_many_arguments(self):
        self.cmd('login.hashed', 'f00', 'f00')



    @expect_error('InvalidArguments')
    def test_logout__too_many_arguments(self):
        self.cmd('logout', 'f00')



    @expect_error('InvalidArguments')
    def test_quit__too_many_arguments(self):
        self.cmd('quit', 'f00')



    def test_version(self):
        self.assertEqual(['BF3', R19_version], self.cmd('version'))

    @expect_error('InvalidArguments')
    def test_version__InvalidArguments(self):
        self.cmd('version', 'f00')




    def test_listplayers__all_nominal(self):
        res = self.cmd('listPlayers', 'all')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_listplayers__team_nominal(self):
        res = self.cmd('listPlayers', 'team', '0')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_listplayers__squad_nominal(self):
        res = self.cmd('listPlayers', 'squad', '0', '0')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_listplayers__player_nominal(self):
        res = self.cmd('listPlayers', 'player', 'f00')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', '0'], res)



    @expect_error('InvalidArguments')
    def test_listplayers__no_argument(self):
        self.cmd('listPlayers')

    @expect_error('InvalidArguments')
    def test_listplayers__too_many_arguments(self):
        self.cmd('listPlayers', 'f00', 'f00', 'f00', 'f00')

    @expect_error('InvalidArguments')
    def test_listplayers__bad_argument(self):
        self.cmd('listPlayers', 'f00')

    @expect_error('InvalidArguments')
    def test_listplayers__no_argument(self):
        self.cmd('listPlayers')

    @expect_error('InvalidArguments')
    def test_listplayers__all_and_junk(self):
        self.cmd('listPlayers', 'all', 'f00')

    @expect_error('InvalidArguments')
    def test_listplayers__team_no_team_number(self):
        self.cmd('listPlayers', 'team')

    @expect_error('InvalidArguments')
    def test_listplayers__team_and_junk(self):
        self.cmd('listPlayers', 'team', 'f00')

    @expect_error('InvalidArguments')
    def test_listplayers__squad_no_team_number(self):
        self.cmd('listPlayers', 'squad')

    @expect_error('InvalidArguments')
    def test_listplayers__squad_and_junk(self):
        self.cmd('listPlayers', 'squad', 'f00')

    @expect_error('InvalidArguments')
    def test_listplayers__squad_no_squad_number(self):
        self.cmd('listPlayers', 'squad', '0')

    @expect_error('InvalidArguments')
    def test_listplayers__squad_too_many_arguments(self):
        self.cmd('listPlayers', 'squad', '0', '0', '0', '0')

    @expect_error('InvalidArguments')
    def test_listplayers__player_and_no_player_name(self):
        self.cmd('listPlayers', 'player')

    @expect_error('InvalidArguments')
    def test_listplayers__player_too_many_arguments(self):
        self.cmd('listPlayers', 'player', 'f00', 'fOO')



    @unittest.skipIf(skip_time_consuming_tests, 'skipping time consumming test')
    def test_not_allowed_commands_raise_LogInRequired(self):
        all_commands = ('admin.eventsEnabled', 'admin.help', 'admin.kickPlayer', 'admin.killPlayer', 'admin.listPlayers',
                        'admin.movePlayer', 'admin.password', 'admin.say', 'admin.shutDown', 'banList.add', 'banList.clear',
                        'banList.list', 'banList.load', 'banList.remove', 'banList.save', 'currentLevel', 'gameAdmin.add',
                        'gameAdmin.clear', 'gameAdmin.list', 'gameAdmin.load', 'gameAdmin.remove', 'gameAdmin.save', 'listPlayers',
                        'login.hashed', 'login.plainText', 'logout', 'mapList.add' ,'mapList.availableMaps', 'mapList.clear',
                        'mapList.endRound', 'mapList.getMapIndices', 'mapList.getRounds', 'mapList.list', 'mapList.load',
                        'mapList.remove', 'mapList.restartRound', 'mapList.runNextRound', 'mapList.save', 'mapList.setNextMapIndex',
                        'punkBuster.activate', 'punkBuster.isActive', 'punkBuster.pb_sv_command',
                        # 'quit',
                        'reservedSlotsList.add', 'reservedSlotsList.clear', 'reservedSlotsList.list', 'reservedSlotsList.load',
                        'reservedSlotsList.remove', 'reservedSlotsList.save', 'serverInfo', 'unlockList.add', 'unlockList.clear',
                        'unlockList.list', 'unlockList.remove', 'unlockList.save', 'vars.3dSpotting', 'vars.3pCam', 'vars.autoBalance',
                        'vars.bannerUrl', 'vars.bulletDamage', 'vars.friendlyFire', 'vars.gameModeCounter', 'vars.gamePassword',
                        'vars.hud', 'vars.idleBanRounds', 'vars.idleTimeout', 'vars.killCam', 'vars.killRotation', 'vars.maxPlayers',
                        'vars.minimap', 'vars.miniMapSpotting', 'vars.nameTag', 'vars.onlySquadLeaderSpawn', 'vars.playerManDownTime',
                        'vars.playerRespawnTime', 'vars.ranked', 'vars.regenerateHealth', 'vars.roundRestartPlayerCount', 'vars.roundsPerMap',
                        'vars.roundStartPlayerCount', 'vars.serverDescription', 'vars.serverMessage', 'vars.serverName', 'vars.soldierHealth',
                        'vars.teamKillCountForKick', 'vars.teamKillKickForBan', 'vars.teamKillValueDecreasePerSecond', 'vars.teamKillValueForKick',
                        'vars.teamKillValueIncrease', 'vars.unlockMode', 'vars.vehicleSpawnAllowed', 'vars.vehicleSpawnDelay', 'version',
            )


        class CommanderThread(threading.Thread):
            todo = Queue.Queue(maxsize=len(all_commands))
            results = Queue.Queue(maxsize=len(all_commands))

            def run(self):
                try:
                    while True:
                        cmd = self.__class__.todo.get(timeout=2)
                        try:
                            self.__class__.t_conn.command(cmd)
                        except CommandFailedError, err:
                            self.__class__.results.put((cmd, err.message[0]))
                        else:
                            self.__class__.results.put((cmd, 'OK'))
                except Queue.Empty:
                    pass
        CommanderThread.t_conn = self.t_conn

        for c in all_commands:
            CommanderThread.todo.put(c, block=False)

        # start 6 threads to run the commands
        threads = []
        for i in range(6):
            t = CommanderThread()
            threads.append(t)
            t.start()

        # wait for all threads to end
        for t in threads:
            t.join()

        # prepare results
        results = dict()
        try:
            while True:
                cmd, res = CommanderThread.results.get(timeout=1)
                results[cmd] = res
        except Queue.Empty:
            pass

        old_maxDiff = self.maxDiff
        self.maxDiff = None
        self.assertDictEqual({
            'admin.eventsEnabled': 'LogInRequired',
            'admin.help': 'LogInRequired',
            'admin.kickPlayer': 'LogInRequired',
            'admin.killPlayer': 'LogInRequired',
            'admin.listPlayers': 'LogInRequired',
            'admin.movePlayer': 'LogInRequired',
            'admin.password': 'LogInRequired',
            'admin.say': 'LogInRequired',
            'admin.shutDown': 'LogInRequired',
            'banList.add': 'LogInRequired',
            'banList.clear': 'LogInRequired',
            'banList.list': 'LogInRequired',
            'banList.load': 'LogInRequired',
            'banList.remove': 'LogInRequired',
            'banList.save': 'LogInRequired',
            'currentLevel': 'LogInRequired',
            'gameAdmin.add': 'LogInRequired',
            'gameAdmin.clear': 'LogInRequired',
            'gameAdmin.list': 'LogInRequired',
            'gameAdmin.load': 'LogInRequired',
            'gameAdmin.remove': 'LogInRequired',
            'gameAdmin.save': 'LogInRequired',
            'listPlayers': 'InvalidArguments',
            'login.hashed': 'OK',
            'login.plainText': 'InvalidArguments',
            'logout': 'OK',
            'mapList.add': 'LogInRequired',
            'mapList.availableMaps': 'LogInRequired',
            'mapList.clear': 'LogInRequired',
            'mapList.endRound': 'LogInRequired',
            'mapList.getMapIndices': 'LogInRequired',
            'mapList.getRounds': 'LogInRequired',
            'mapList.list': 'LogInRequired',
            'mapList.load': 'LogInRequired',
            'mapList.remove': 'LogInRequired',
            'mapList.restartRound': 'LogInRequired',
            'mapList.runNextRound': 'LogInRequired',
            'mapList.save': 'LogInRequired',
            'mapList.setNextMapIndex': 'LogInRequired',
            'punkBuster.activate': 'LogInRequired',
            'punkBuster.isActive': 'LogInRequired',
            'punkBuster.pb_sv_command': 'LogInRequired',
            'reservedSlotsList.add': 'LogInRequired',
            'reservedSlotsList.clear': 'LogInRequired',
            'reservedSlotsList.list': 'LogInRequired',
            'reservedSlotsList.load': 'LogInRequired',
            'reservedSlotsList.remove': 'LogInRequired',
            'reservedSlotsList.save': 'LogInRequired',
            'serverInfo': 'OK',
            'unlockList.add': 'LogInRequired',
            'unlockList.clear': 'LogInRequired',
            'unlockList.list': 'LogInRequired',
            'unlockList.remove': 'LogInRequired',
            'unlockList.save': 'LogInRequired',
            'vars.3dSpotting': 'LogInRequired',
            'vars.3pCam': 'LogInRequired',
            'vars.autoBalance': 'LogInRequired',
            'vars.bannerUrl': 'LogInRequired',
            'vars.bulletDamage': 'LogInRequired',
            'vars.friendlyFire': 'LogInRequired',
            'vars.gameModeCounter': 'LogInRequired',
            'vars.gamePassword': 'LogInRequired',
            'vars.hud': 'LogInRequired',
            'vars.idleBanRounds': 'LogInRequired',
            'vars.idleTimeout': 'LogInRequired',
            'vars.killCam': 'LogInRequired',
            'vars.killRotation': 'LogInRequired',
            'vars.maxPlayers': 'LogInRequired',
            'vars.minimap': 'LogInRequired',
            'vars.miniMapSpotting': 'LogInRequired',
            'vars.nameTag': 'LogInRequired',
            'vars.onlySquadLeaderSpawn': 'LogInRequired',
            'vars.playerManDownTime': 'LogInRequired',
            'vars.playerRespawnTime': 'LogInRequired',
            'vars.ranked': 'LogInRequired',
            'vars.regenerateHealth': 'LogInRequired',
            'vars.roundRestartPlayerCount': 'LogInRequired',
            'vars.roundsPerMap': 'LogInRequired',
            'vars.roundStartPlayerCount': 'LogInRequired',
            'vars.serverDescription': 'LogInRequired',
            'vars.serverMessage': 'LogInRequired',
            'vars.serverName': 'LogInRequired',
            'vars.soldierHealth': 'LogInRequired',
            'vars.teamKillCountForKick': 'LogInRequired',
            'vars.teamKillKickForBan': 'LogInRequired',
            'vars.teamKillValueDecreasePerSecond': 'LogInRequired',
            'vars.teamKillValueForKick': 'LogInRequired',
            'vars.teamKillValueIncrease': 'LogInRequired',
            'vars.unlockMode': 'LogInRequired',
            'vars.vehicleSpawnAllowed': 'LogInRequired',
            'vars.vehicleSpawnDelay': 'LogInRequired',
            'version': 'OK'
        }, results)
        self.maxDiff = old_maxDiff


if __name__ == '__main__':
    unittest.main()