# -*- encoding: utf-8 -*-
import unittest
from lib.bf3testutils import *
load_config_file()



# names of variables that accept boolean values as input
boolean_var_names = ('autoBalance', 'friendlyFire', 'killCam', 'miniMap', 'hud', '3dSpotting',
                     'nameTag', '3pCam', 'regenerateHealth', 'vehicleSpawnAllowed', 'onlySquadLeaderSpawn')



class Test_ranked(BF3_authenticated_TestCase):
    ## vars.ranked [ranked: boolean]

    def test_no_argument(self):
        self.assertIn(self.cmd('vars.ranked'), (['true'], ['false']))

    @expect_error('CommandIsReadOnly')
    def test_true(self):
        self.cmd('vars.ranked', 'true')

    @expect_error('CommandIsReadOnly')
    def test_false(self):
        self.cmd('vars.ranked', 'false')




class Test_misc(BF3_authenticated_TestCase):


    def assert_set(self, var_name, data, expected_data=None):
        """
        assert that setting data for var_name works and does set data or expected_data is provided.
        """
        # set new data
        print "vars.%s '%s'" % (var_name, data)
        self.cmd('vars.%s' % var_name, data)

        # verify new data is correctly set
        actual, = self.cmd('vars.%s' % var_name)
        if expected_data:
            self.assertEqual(expected_data, actual, "expecting vars.%s '%s' to set '%s'. Got '%s' instead" % (var_name, data, expected_data, actual))
        else:
            self.assertEqual(data, actual, "expecting vars.%s '%s' to set '%s'. Got '%s' instead" % (var_name, data, data, actual))



    ## vars.serverName [name: string]
    def test_serverName(self):
        self.assert_set('serverName', 'f00')


    ## vars.gamePassword [password: password]
    @unittest.skipIf(Bf3_test_config.ranked, "server is ranked")
    @expect_error('CommandIsReadOnly')
    def test_gamePassword_unranked(self):
        self.assert_set('gamePassword', 'f00')

    @unittest.skipUnless(Bf3_test_config.ranked, "server is not ranked")
    @expect_error('CommandDisallowedOnRanked')
    def test_gamePassword_ranked(self):
        original, = self.cmd('vars.gamePassword')
        self.cmd('vars.gamePassword', 'f00')
        # restore
        self.cmd('vars.gamePassword', original)



    ## vars.maxPlayers [nr of players: integer]
    def test_maxPlayers(self):
        self.assert_set('maxPlayers', '0')
        self.assert_set('maxPlayers', '1')
        self.assert_set('maxPlayers', '4')
        self.assert_set('maxPlayers', '8')
        self.assert_set('maxPlayers', '16')

    @expect_error('InvalidMaxPlayerCount')
    def test_maxPlayers_too_high(self):
        self.cmd('vars.maxPlayers', '33')

    @expect_error('InvalidArguments')
    def test_maxPlayers_bad_argument(self):
        self.cmd('vars.maxPlayers', 'f00')

    @expect_error('InvalidArguments')
    def test_maxPlayers_too_many_arguments(self):
        self.cmd('vars.maxPlayers', '8', 'f00')




    ## vars.teamKillCountForKick [count: integer]
    def test_teamKillCountForKick(self):
        self.assert_set('teamKillCountForKick', '0')
        self.assert_set('teamKillCountForKick', '1')
        self.assert_set('teamKillCountForKick', '4')
        self.assert_set('teamKillCountForKick', '8')
        self.assert_set('teamKillCountForKick', '16')

    @expect_error('InvalidArguments')
    def test_teamKillCountForKick_bad_argument(self):
        self.cmd('vars.teamKillCountForKick', 'f00')

    @expect_error('InvalidArguments')
    def test_teamKillCountForKick_too_many_arguments(self):
        self.cmd('vars.teamKillCountForKick', '8', 'f00')



    ## vars.teamKillValueForKick [count: integer]
    def test_teamKillValueForKick(self):
        self.assert_set('teamKillValueForKick', '0')
        self.assert_set('teamKillValueForKick', '1')
        self.assert_set('teamKillValueForKick', '1.5')
        self.assert_set('teamKillValueForKick', '8')

    @expect_error('InvalidArguments')
    def test_teamKillValueForKick_bad_argument(self):
        self.cmd('vars.teamKillValueForKick', 'f00')

    @expect_error('InvalidArguments')
    def test_teamKillValueForKick_too_many_arguments(self):
        self.cmd('vars.teamKillValueForKick', '8', 'f00')




    ## vars.teamKillValueIncrease [count: integer]
    def test_teamKillValueIncrease(self):
        self.assert_set('teamKillValueIncrease', '0')
        self.assert_set('teamKillValueIncrease', '1')
        self.assert_set('teamKillValueIncrease', '1.5')
        self.assert_set('teamKillValueIncrease', '8')

    @expect_error('InvalidArguments')
    def test_teamKillValueIncrease_bad_argument(self):
        self.cmd('vars.teamKillValueIncrease', 'f00')

    @expect_error('InvalidArguments')
    def test_teamKillValueIncrease_too_many_arguments(self):
        self.cmd('vars.teamKillValueIncrease', '8', 'f00')





    ## vars.teamKillValueDecreasePerSecond [count: integer]
    def test_teamKillValueDecreasePerSecond(self):
        self.assert_set('teamKillValueDecreasePerSecond', '0')
        self.assert_set('teamKillValueDecreasePerSecond', '1')
        self.assert_set('teamKillValueDecreasePerSecond', '1.5')
        self.assert_set('teamKillValueDecreasePerSecond', '8')

    @expect_error('InvalidArguments')
    def test_teamKillValueDecreasePerSecond_bad_argument(self):
        self.cmd('vars.teamKillValueDecreasePerSecond', 'f00')

    @expect_error('InvalidArguments')
    def test_teamKillValueDecreasePerSecond_too_many_arguments(self):
        self.cmd('vars.teamKillValueDecreasePerSecond', '8', 'f00')





    ## vars.teamKillKickForBan [count: integer]
    def test_teamKillKickForBan(self):
        self.assert_set('teamKillKickForBan', '0')
        self.assert_set('teamKillKickForBan', '1')
        self.assert_set('teamKillKickForBan', '1.5', '1')
        self.assert_set('teamKillKickForBan', '8')

    @expect_error('InvalidArguments')
    def test_teamKillKickForBan_bad_argument(self):
        self.cmd('vars.teamKillKickForBan', 'f00')

    @expect_error('InvalidArguments')
    def test_teamKillKickForBan_too_many_arguments(self):
        self.cmd('vars.teamKillKickForBan', '8', 'f00')





    ## vars.idleTimeout [count: integer]
    def test_idleTimeout(self):
        self.assert_set('idleTimeout', '0')
        self.assert_set('idleTimeout', '1')
        self.assert_set('idleTimeout', '1.5', '1')
        self.assert_set('idleTimeout', '8')

    @expect_error('InvalidArguments')
    def test_idleTimeout_bad_argument(self):
        self.cmd('vars.idleTimeout', 'f00')

    @expect_error('InvalidArguments')
    def test_idleTimeout_too_many_arguments(self):
        self.cmd('vars.idleTimeout', '8', 'f00')



    ## vars.idleBanRounds [count: integer]
    def test_idleBanRounds(self):
        self.assert_set('idleBanRounds', '0')
        self.assert_set('idleBanRounds', '1')
        self.assert_set('idleBanRounds', '1.5', '1')
        self.assert_set('idleBanRounds', '8')

    @expect_error('InvalidArguments')
    def test_idleBanRounds_bad_argument(self):
        self.cmd('vars.idleBanRounds', 'f00')

    @expect_error('InvalidArguments')
    def test_idleBanRounds_too_many_arguments(self):
        self.cmd('vars.idleBanRounds', '8', 'f00')




    ## vars.roundLockdownCountdown [time: seconds]
    def test_roundLockdownCountdown_too_small(self):
        self.assert_set('roundLockdownCountdown', '9', '10')

    @unittest.skipUnless(Bf3_test_config.ranked, "server is not ranked")
    def test_roundLockdownCountdown_too_big_on_ranked(self):
        self.assert_set('roundLockdownCountdown', '31', '30')

    @unittest.skipIf(Bf3_test_config.ranked, "server is ranked")
    def test_roundLockdownCountdown_too_big_on_unranked(self):
        self.assert_set('roundLockdownCountdown', '901', '900')

    def test_roundLockdownCountdown(self):
        self.assert_set('roundLockdownCountdown', '10')
        self.assert_set('roundLockdownCountdown', '30')

    def test_roundLockdownCounddown_float_value(self):
        self.assert_set('roundLockdownCountdown', '11.54', '11')

    @expect_error('InvalidArguments')
    def test_roundStartPlayerCount_bad_argument(self):
        self.cmd('vars.roundLockdownCountdown', 'f00')

    @expect_error('InvalidArguments')
    def test_roundStartPlayerCount_too_many_arguments(self):
        self.cmd('vars.roundLockdownCountdown', '11', 'f00')



    ## vars.roundStartPlayerCount [count: integer]
    @expect_error('InvalidValue')
    def test_roundStartPlayerCount_zero(self):
        self.assert_set('roundStartPlayerCount', '0')

    def test_roundStartPlayerCount(self):
        self.assert_set('roundStartPlayerCount', '1')
        self.assert_set('roundStartPlayerCount', '1.5', '1')
        self.assert_set('roundStartPlayerCount', '8')

    @expect_error('InvalidArguments')
    def test_roundStartPlayerCount_bad_argument(self):
        self.cmd('vars.roundStartPlayerCount', 'f00')

    @expect_error('InvalidArguments')
    def test_roundStartPlayerCount_too_many_arguments(self):
        self.cmd('vars.roundStartPlayerCount', '8', 'f00')



    ## vars.roundRestartPlayerCount [count: integer]
    def test_roundRestartPlayerCount(self):
        self.assert_set('roundRestartPlayerCount', '0')
        self.assert_set('roundRestartPlayerCount', '1')
        self.assert_set('roundRestartPlayerCount', '1.5', '1')

    @expect_error('InvalidArguments')
    def test_roundRestartPlayerCount_bad_argument(self):
        self.cmd('vars.roundRestartPlayerCount', 'f00')

    @expect_error('InvalidArguments')
    def test_roundRestartPlayerCount_too_many_arguments(self):
        self.cmd('vars.roundRestartPlayerCount', '8', 'f00')



    ## vars.serverDescription [description: string]
    def test_serverDescription(self):
        self.assert_set('roundRestartPlayerCount', 'test server description')
        self.assert_set('roundRestartPlayerCount', '')

    @expect_error('InvalidArguments')
    def test_serverDescription_too_many_arguments(self):
        self.cmd('vars.roundRestartPlayerCount', 'test server description', 'f00')



    ## vars.unlockMode [mode: Unlock mode]
    def test_unlockMode(self):
        self.assert_set('unlockMode', 'all')
        self.assert_set('unlockMode', 'common')
        self.assert_set('unlockMode', 'stats')
        self.assert_set('unlockMode', 'none')

    @expect_error('InvalidArguments')
    def test_unlockMode_bad_argument(self):
        self.cmd('vars.unlockMode', 'f00')

    @expect_error('InvalidArguments')
    def test_unlockMode_too_many_arguments(self):
        self.cmd('vars.unlockMode', 'all', 'f00')




class Test_scale_factor(BF3_authenticated_TestCase):

    # list of (input, expected)
    test_values = [('0','0'), ('100','100'), ('80','80'), ('50','50'), ('5', '5'), ('0.4','0')]



    ## vars.vehicleSpawnDelay [modifier: percent]

    def test_vehicleSpawnDelay_nominal(self):
        for data, expected in self.test_values:
            # set new data
            self.cmd('vars.vehicleSpawnDelay', data)
            # verify new data is correctly set
            actual, = self.cmd('vars.vehicleSpawnDelay')
            self.assertEqual(expected, actual, "vars.vehicleSpawnDelay '%s' failed, expecting '%s', got '%s' instead" % (data, expected, actual))

    def test_vehicleSpawnDelay_1(self):
        self.cmd('vars.vehicleSpawnDelay', '1')
        actual, = self.cmd('vars.vehicleSpawnDelay')
        self.assertEqual('1', actual, "vars.vehicleSpawnDelay '1', got '%s' instead" % actual)

    def test_vehicleSpawnDelay_2(self):
        self.cmd('vars.vehicleSpawnDelay', '2')
        actual, = self.cmd('vars.vehicleSpawnDelay')
        self.assertEqual('2', actual, "vars.vehicleSpawnDelay '2', got '%s' instead" % actual)

    def test_vehicleSpawnDelay_3(self):
        self.cmd('vars.vehicleSpawnDelay', '3')
        actual, = self.cmd('vars.vehicleSpawnDelay')
        self.assertEqual('3', actual, "vars.vehicleSpawnDelay '3', got '%s' instead" % actual)

    def test_vehicleSpawnDelay_4(self):
        self.cmd('vars.vehicleSpawnDelay', '4')
        actual, = self.cmd('vars.vehicleSpawnDelay')
        self.assertEqual('4', actual, "vars.vehicleSpawnDelay '4', got '%s' instead" % actual)

    @expect_error('InvalidArguments')
    def test_vehicleSpawnDelay_bad_data(self):
        self.cmd('vars.vehicleSpawnDelay', 'f**')

    @expect_error('InvalidArguments')
    def test_vehicleSpawnDelay_too_many_arguments(self):
        self.cmd('vars.vehicleSpawnDelay', '1', 'f00')



    ## vars.soldierHealth [modifier: percent]

    def test_soldierHealth_nominal(self):
        for data, expected in self.test_values:
            # set new data
            self.cmd('vars.soldierHealth', data)
            # verify new data is correctly set
            actual, = self.cmd('vars.soldierHealth')
            self.assertEqual(expected, actual, "vars.soldierHealth '%s' failed, expecting '%s', got '%s' instead" % (data, expected, actual))

    @expect_error('InvalidArguments')
    def test_soldierHealth_bad_data(self):
        self.cmd('vars.soldierHealth', 'f**')

    @expect_error('InvalidArguments')
    def test_soldierHealth_too_many_arguments(self):
        self.cmd('vars.soldierHealth', '1', 'f00')



    ## vars.playerRespawnTime [modifier: percent]

    def test_playerRespawnTime_nominal(self):
        for data, expected in self.test_values:
            # set new data
            self.cmd('vars.playerRespawnTime', data)
            # verify new data is correctly set
            actual, = self.cmd('vars.playerRespawnTime')
            self.assertEqual(expected, actual, "vars.playerRespawnTime '%s' failed, expecting '%s', got '%s' instead" % (data, expected, actual))

    @expect_error('InvalidArguments')
    def test_playerRespawnTime_bad_data(self):
        self.cmd('vars.playerRespawnTime', 'f**')

    @expect_error('InvalidArguments')
    def test_playerRespawnTime_too_many_arguments(self):
        self.cmd('vars.playerRespawnTime', '1', 'f00')



    ## vars.gameModeCounter [modifier: percent]

    def test_gameModeCounter_nominal(self):
        for data, expected in self.test_values:
            # set new data
            self.cmd('vars.gameModeCounter', data)
            # verify new data is correctly set
            actual, = self.cmd('vars.gameModeCounter')
            self.assertEqual(expected, actual, "vars.gameModeCounter '%s' failed, expecting '%s', got '%s' instead" % (data, expected, actual))

    @expect_error('InvalidArguments')
    def test_gameModeCounter_bad_data(self):
        self.cmd('vars.gameModeCounter', 'f**')

    @expect_error('InvalidArguments')
    def test_gameModeCounter_too_many_arguments(self):
        self.cmd('vars.gameModeCounter', '1', 'f00')



    ## vars.bulletDamage [modifier: percent]

    def test_bulletDamage_nominal(self):
        for data, expected in self.test_values:
            # set new data
            self.cmd('vars.bulletDamage', data)
            # verify new data is correctly set
            actual, = self.cmd('vars.bulletDamage')
            self.assertEqual(expected, actual, "vars.bulletDamage '%s' failed, expecting '%s', got '%s' instead" % (data, expected, actual))

    @expect_error('InvalidArguments')
    def test_bulletDamage_bad_data(self):
        self.cmd('vars.bulletDamage', 'f**')

    @expect_error('InvalidArguments')
    def test_bulletDamage_too_many_arguments(self):
        self.cmd('vars.bulletDamage', '1', 'f00')



    ## vars.playerManDownTime [modifier: percent]

    def test_playerManDownTime_nominal(self):
        for data, expected in self.test_values:
            # set new data
            self.cmd('vars.bulletDamage', data)
            # verify new data is correctly set
            actual, = self.cmd('vars.bulletDamage')
            self.assertEqual(expected, actual, "vars.bulletDamage '%s' failed, expecting '%s', got '%s' instead" % (data, expected, actual))

    @expect_error('InvalidArguments')
    def test_bulletDamage_bad_data(self):
        self.cmd('vars.bulletDamage', 'f**')

    @expect_error('InvalidArguments')
    def test_bulletDamage_too_many_arguments(self):
        self.cmd('vars.bulletDamage', '1', 'f00')






class boolean_test_maker_type(type):
    def __new__(cls, name, bases, dct):
        for var_name in boolean_var_names:
            dct['test_%s_nominal' % var_name] = boolean_test_maker_type.nominal_test(var_name)
            dct['test_%s_bad_data' % var_name] = boolean_test_maker_type.bad_data_test(var_name)
            dct['test_%s_too_many_arguments' % var_name] = boolean_test_maker_type.too_many_arguments(var_name)
        return type.__new__(cls, name, bases, dct)


    @staticmethod
    def nominal_test(var_name):
        def f(self):
            for data, expected in [('true','true'), ('false','false'), ('1','true'), ('0','false')]:
                # set new data
                self.cmd('vars.%s' % var_name, data)
                # verify new data is correctly set
                actual, = self.cmd('vars.%s' % var_name)
                self.assertEqual(expected, actual, "vars.%s '%s' failed, expecting '%s', got '%s' instead" % (var_name, data, expected, actual))
        return f


    @staticmethod
    def bad_data_test(var_name):
        def f(self):
            try:
                self.cmd('vars.%s' % var_name, 'f**')
            except CommandFailedError, err:
                self.assertEqual(['InvalidArguments'], err.message, "vars.%s 'f**' expected to fail with error 'InvalidArguments', got '%r' instead" % (var_name, err.message))
            else:
                self.fail("expecting InvalidArguments error for : vars.%s 'f***'" % var_name)
        return f


    @staticmethod
    def too_many_arguments(var_name):
        def f(self):
            try:
                self.cmd('vars.%s' % var_name, 'true', 'f**')
            except CommandFailedError, err:
                self.assertEqual(['InvalidArguments'], err.message, "vars.%s 'true' 'f**' expected to fail with error 'InvalidArguments', got '%r' instead" % (var_name, err.message))
            else:
                self.fail("expecting InvalidArguments error for : vars.%s 'true' 'f***'" % var_name)
        return f


class Test_boolean(BF3_authenticated_TestCase):
    __metaclass__ = boolean_test_maker_type


    ## miniMapSpotting
    def test_miniMapSpotting_get(self):
        self.assertIn(self.cmd('vars.miniMapSpotting'), (['true'], ['false']))

    @expect_error('CommandIsReadOnly')
    def test_miniMapSpotting_set(self):
        self.cmd('vars.miniMapSpotting', 'true')


