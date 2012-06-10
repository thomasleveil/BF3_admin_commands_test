# -*- encoding: utf-8 -*-
import threading, Queue, re
import unittest
from lib.protocol import generatePasswordHash
from lib.bf3testutils import *

load_config_file()


class Test_misc(BF3_connected_TestCase):

    @expect_error('UnknownCommand')
    def test_unknown_command(self):
        self.cmd('f00')


    @expect_error('InvalidArguments')
    def test_quit__too_many_arguments(self):
        self.cmd('quit', 'f00')


    def test_version(self):
        self.assertEqual(['BF3', '926998'], self.cmd('version'))

    @expect_error('InvalidArguments')
    def test_version__InvalidArguments(self):
        self.cmd('version', 'f00')




class Test_login_logout(BF3_connected_TestCase):

    def test_login_plainText__and__logout__nominal(self):
        # verify that we are not logged in
        try:
            self.cmd('admin.listPlayers')
        except CommandFailedError, err:
            if err.message[0] != 'LogInRequired':
                self.fail('expecting to be logged out')

        # try to authenticate
        res = self.cmd('login.plainText', Bf3_test_config.pw)

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
        passwordHash = generatePasswordHash(salt, Bf3_test_config.pw)
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
        self.cmd('login.plainText', Bf3_test_config.pw, 'f00')

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



class Test_listplayers(BF3_connected_TestCase):

    def test_all_nominal(self):
        res = self.cmd('listPlayers', 'all')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_team_nominal(self):
        res = self.cmd('listPlayers', 'team', '0')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_squad_nominal(self):
        res = self.cmd('listPlayers', 'squad', '0', '0')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score'], res[:8])

    def test_player_nominal(self):
        res = self.cmd('listPlayers', 'player', 'f00')
        self.assertEqual(['7', 'name', 'guid', 'teamId', 'squadId', 'kills', 'deaths', 'score', '0'], res)



    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('listPlayers')

    @expect_error('InvalidArguments')
    def test_too_many_arguments(self):
        self.cmd('listPlayers', 'f00', 'f00', 'f00', 'f00')

    @expect_error('InvalidArguments')
    def test_bad_argument(self):
        self.cmd('listPlayers', 'f00')

    @expect_error('InvalidArguments')
    def test_no_argument(self):
        self.cmd('listPlayers')

    @expect_error('InvalidArguments')
    def test_all_and_junk(self):
        self.cmd('listPlayers', 'all', 'f00')

    @expect_error('InvalidArguments')
    def test_team_no_team_number(self):
        self.cmd('listPlayers', 'team')

    @expect_error('InvalidArguments')
    def test_team_and_junk(self):
        self.cmd('listPlayers', 'team', 'f00')

    @expect_error('InvalidArguments')
    def test_squad_no_team_number(self):
        self.cmd('listPlayers', 'squad')

    @expect_error('InvalidArguments')
    def test_squad_and_junk(self):
        self.cmd('listPlayers', 'squad', 'f00')

    @expect_error('InvalidArguments')
    def test_squad_no_squad_number(self):
        self.cmd('listPlayers', 'squad', '0')

    @expect_error('InvalidArguments')
    def test_squad_too_many_arguments(self):
        self.cmd('listPlayers', 'squad', '0', '0', '0', '0')

    @expect_error('InvalidArguments')
    def test_player_and_no_player_name(self):
        self.cmd('listPlayers', 'player')

    @expect_error('InvalidArguments')
    def test_player_too_many_arguments(self):
        self.cmd('listPlayers', 'player', 'f00', 'fOO')



class Test_login_required(BF3_authenticated_TestCase):

    @unittest.skipIf(Bf3_test_config.skip_time_consuming_tests, 'skipping time consumming test')
    def test_not_allowed_commands_raise_LogInRequired(self):
        all_commands = [x for x in self.cmd('admin.help') if x not in ('quit',
                                    'admin.teamSwitchPlayer', 'vars.roundWarmupTimeout' # undocumented
            )]
        self.cmd('logout')

        class CommanderThread(threading.Thread):
            todo = Queue.Queue(maxsize=len(all_commands))
            results = Queue.Queue(maxsize=len(all_commands))

            def run(self):
                try:
                    while True:
                        cmd = self.__class__.todo.get(timeout=2)
                        try:
                            print repr(cmd)
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
            'admin.yell': 'LogInRequired',
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
            'reservedSlotsList.aggressiveJoin': 'LogInRequired',
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
            'unlockList.set': 'LogInRequired',
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
            'vars.premiumStatus': 'LogInRequired',
            'vars.ranked': 'LogInRequired',
            'vars.regenerateHealth': 'LogInRequired',
            'vars.roundLockdownCountdown': 'LogInRequired',
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

