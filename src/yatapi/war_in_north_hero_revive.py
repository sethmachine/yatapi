"""

"""

import collections
import json

import sccount
import scoperation
import scplayer
import scquantifier
import scresource
import scunit
import trigger
from trigger import Trigger
from trigger_statements import *


SYSTEM_NAME = 'Hero Revival'
CIV_RETURN_LOCATION = 'civreturn'
BUY_HERO_LOCATION = 'buy hero revive'
BUY_UNIT = scunit.TERRAN_CIVILIAN
REVIVE_COST = 250
TRIG_PLAYER = scplayer.ALL_PLAYERS
PLAYER = scplayer.CURRENT_PLAYER
REVIVE_MSG = 'Your hero has been revived!'

DATA = collections.defaultdict(dict)
DATA['P1']['loc'] = 'spawnNorgon'
DATA['P2']['loc'] = 'spawnmaryadenn'
DATA['P3']['loc'] = 'spawnport'
DATA['P4']['loc'] = 'ProvenceSpawn'
DATA['P5']['loc'] = 'spawnorange'
DATA['P6']['loc'] = 'MordorSpawn'
DATA['P8']['loc'] = 'spawngreen'

DATA['P1']['building'] = scunit.PSI_DISRUPTER
DATA['P2']['building'] = scunit.XELNAGA_TEMPLE
DATA['P3']['building'] = scunit.NORAD_II_CRASHED_BATTLECRUISER
DATA['P4']['building'] = scunit.ION_CANNON
DATA['P5']['building'] = scunit.ZERG_OVERMIND
DATA['P6']['building'] = scunit.ZERG_OVERMIND_WITH_SHELL
DATA['P8']['building'] = scunit.PROTOSS_TEMPLE

DATA['P1']['heroes'] = [scunit.ALAN_SCHEZAR_GOLIATH, scunit.ALEXEI_STUKOV_GHOST,
                        scunit.GUI_MONTAG_FIREBAT]
DATA['P2']['heroes'] = [scunit.JIM_RAYNOR_VULTURE, scunit.FENIX_DRAGOON]
DATA['P3']['heroes'] = [scunit.PROTOSS_ARBITER, scunit.SAMIR_DURAN_GHOST]
DATA['P4']['heroes'] = [scunit.JIM_RAYNOR_MARINE]
DATA['P5']['heroes'] = [scunit.HUNTER_KILLER_HYDRALISK, scunit.INFESTED_DURAN]
DATA['P6']['heroes'] = [scunit.ZERATUL_DARK_TEMPLAR, scunit.TOM_KAZANSKY_WRAITH]
DATA['P8']['heroes'] = [scunit.INFESTED_KERRIGAN_INFESTED_TERRAN, scunit.TORRASQUE_ULTRALISK,
                         scunit.KUKULZA_MUTALISK, scunit.UNCLEAN_ONE_DEFILER]


class ReviveTrigger:
    def __init__(self, hero: scunit.SCUnit, required_building: scunit.SCUnit,
                 revive_location: str, player: scplayer.SCPlayer=PLAYER, trig_player: scplayer.SCPlayer=TRIG_PLAYER,
                 buy_unit: scunit.SCUnit=BUY_UNIT ,
                 buy_location: str=BUY_HERO_LOCATION, return_location: str=CIV_RETURN_LOCATION,
                 cost: int=REVIVE_COST, msg: str=REVIVE_MSG, system: str=SYSTEM_NAME):
        self.player = player
        self.trig_player = trig_player
        self.buy_unit = buy_unit
        self.buy_location = buy_location
        self.return_location = return_location
        self.cost = cost
        self.msg = msg
        self.hero = hero
        self.required_building = required_building
        self.revive_location = revive_location
        self.system = system

    def create(self):
        conditions = [Bring(self.player, self.buy_unit, self.buy_location,
                            scquantifier.EXACTLY, 1),
                      Accumulate(self.player, scquantifier.AT_LEAST, amount=self.cost,
                                 resource=scresource.ORE),
                      Command(self.player, self.required_building, scquantifier.EXACTLY, 1),
                      Command(self.player, self.hero, scquantifier.EXACTLY, 0)]

        actions = [DisplayTextMessage(text=self.msg),
                   CreateUnit(self.player, self.hero, 1, self.revive_location),
                   SetResources(self.player, scoperation.SUBTRACT, self.cost, scresource.ORE),
                   MoveUnit(self.player, self.buy_unit, sccount.ALL,
                            self.buy_location, self.return_location),
                   PreserveTrigger()]
        trig = Trigger([self.trig_player], conditions, actions)
        return trig


def create_revive_triggers(data=DATA):
    triggers = []
    for player_key in data:
        pdata = data[player_key]
        required_building = pdata['building']
        revive_loc = pdata['loc']
        heroes = pdata['heroes']
        for hero in heroes:
            rt = ReviveTrigger(hero, required_building, revive_loc)
            triggers.append(rt.create())
    return triggers


if __name__ == '__main__':
    t = create_revive_triggers(data=DATA)
    revive_system = trigger.compile_triggers(t, {'system': SYSTEM_NAME})
    # revive_sys = '\n\n'.join([x.compile() for x in t])
    outfile = 'data/war-in-the-north/revive_preserve_triggers.txt'
    with open(outfile, 'w') as f:
        f.write(revive_system)
    # with open(outfile, 'w') as f:
    #     f.write(revive_sys.replace('\n', '\r\n'))

