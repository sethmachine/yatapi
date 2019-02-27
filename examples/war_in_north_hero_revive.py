"""Creates triggers to allow players to pay to revive a hero based on what building they control.

"""

import collections
import typing

import yatapi.sccount
import yatapi.scoperation
import yatapi.scplayer
import yatapi.scquantifier
import yatapi.scresource
import yatapi.scunit
import yatapi.trigger
from yatapi.trigger_statements import *

# name of this set of triggers, to make it easy to go back and update if needed
SYSTEM_NAME = 'Hero Revival'
# unit used to purchase by moving to a location
BUY_UNIT = yatapi.scunit.TERRAN_CIVILIAN
# where the buy unit goes after making a purchase to avoid unwanted purchases
CIV_RETURN_LOCATION = 'civreturn'
# location to trigger the buying back of the hero
BUY_HERO_LOCATION = 'buy hero revive'
# mineral cost to revive, easily can change this
REVIVE_COST = 250
# which player the triggers are owned by
TRIG_PLAYER = yatapi.scplayer.ALL_PLAYERS
# who each trigger condition/action actually executes for
PLAYER = yatapi.scplayer.CURRENT_PLAYER
# text message to indicate the hero was successfully revived
REVIVE_MSG = 'Your hero has been revived!'

DATA = collections.defaultdict(dict)
# these locations are hardcoded from the actual map
DATA['P1']['loc'] = 'spawnNorgon'
DATA['P2']['loc'] = 'spawnmaryadenn'
DATA['P3']['loc'] = 'spawnport'
DATA['P4']['loc'] = 'ProvenceSpawn'
DATA['P5']['loc'] = 'spawnorange'
DATA['P6']['loc'] = 'MordorSpawn'
DATA['P8']['loc'] = 'spawngreen'

# these are the main spawn buildings of each player
DATA['P1']['building'] = yatapi.scunit.PSI_DISRUPTER
DATA['P2']['building'] = yatapi.scunit.XELNAGA_TEMPLE
DATA['P3']['building'] = yatapi.scunit.NORAD_II_CRASHED_BATTLECRUISER
DATA['P4']['building'] = yatapi.scunit.ION_CANNON
DATA['P5']['building'] = yatapi.scunit.ZERG_OVERMIND
DATA['P6']['building'] = yatapi.scunit.ZERG_OVERMIND_WITH_SHELL
DATA['P8']['building'] = yatapi.scunit.PROTOSS_TEMPLE

# these are the units used as heroes for each player
DATA['P1']['heroes'] = [yatapi.scunit.ALAN_SCHEZAR_GOLIATH, yatapi.scunit.ALEXEI_STUKOV_GHOST,
                        yatapi.scunit.GUI_MONTAG_FIREBAT]
DATA['P2']['heroes'] = [yatapi.scunit.JIM_RAYNOR_VULTURE, yatapi.scunit.FENIX_DRAGOON]
DATA['P3']['heroes'] = [yatapi.scunit.PROTOSS_ARBITER, yatapi.scunit.SAMIR_DURAN_GHOST]
DATA['P4']['heroes'] = [yatapi.scunit.JIM_RAYNOR_MARINE]
DATA['P5']['heroes'] = [yatapi.scunit.HUNTER_KILLER_HYDRALISK, yatapi.scunit.INFESTED_DURAN]
DATA['P6']['heroes'] = [yatapi.scunit.ZERATUL_DARK_TEMPLAR, yatapi.scunit.TOM_KAZANSKY_WRAITH]
DATA['P8']['heroes'] = [yatapi.scunit.INFESTED_KERRIGAN_INFESTED_TERRAN, yatapi.scunit.TORRASQUE_ULTRALISK,
                        yatapi.scunit.KUKULZA_MUTALISK, yatapi.scunit.UNCLEAN_ONE_DEFILER]


class ReviveTrigger:
    """Wrapper to encapsulate all the parameters for each hero revival trigger.

    """
    def __init__(self, hero: yatapi.scunit.SCUnit, required_building: yatapi.scunit.SCUnit,
                 revive_location: str, player: yatapi.scplayer.SCPlayer=PLAYER, trig_player: yatapi.scplayer.SCPlayer=TRIG_PLAYER,
                 buy_unit: yatapi.scunit.SCUnit=BUY_UNIT ,
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
        """Creates the trigger for reviving a single hero.

        Conditions: player brings a civ to the buy location and has at least 250 minerals,
        and does not control the hero anymore (i.e. it is dead), also checks if the player
        should own the hero based on required building

        Actions: subtract 250 ore, tell the player the hero is revived, re-creates the hero
        at the player's main spawn (different for each player/hero), and moves the civ off the purchase
        location to avoid accidental buybacks.
        :return: a single trigger that handles reviving a hero
        :rtype: yatapi.trigger.Trigger
        """
        conditions = [Bring(self.player, self.buy_unit, self.buy_location,
                            yatapi.scquantifier.EXACTLY, 1),
                      Accumulate(self.player, yatapi.scquantifier.AT_LEAST, amount=self.cost,
                                 resource=yatapi.scresource.ORE),
                      Command(self.player, self.required_building, yatapi.scquantifier.EXACTLY, 1),
                      Command(self.player, self.hero, yatapi.scquantifier.EXACTLY, 0)]

        actions = [DisplayTextMessage(text=self.msg),
                   CreateUnit(self.player, self.hero, 1, self.revive_location),
                   SetResources(self.player, yatapi.scoperation.SUBTRACT, self.cost, yatapi.scresource.ORE),
                   MoveUnit(self.player, self.buy_unit, yatapi.sccount.ALL,
                            self.buy_location, self.return_location),
                   PreserveTrigger()]
        trig = yatapi.trigger.Trigger([self.trig_player], conditions, actions)
        return trig


def create_revive_triggers(data) -> typing.List[yatapi.trigger.Trigger]:
    """Creates hero revival triggers for each player/hero combination.

    :param data: dictionary mapping each player to their spawn building, heroes, and main spawn location
    :type data: dict
    :return:
    """
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
    revive_triggers = create_revive_triggers(data=DATA)
    revive_system = yatapi.trigger.compile_triggers(revive_triggers, jsondata={'system': SYSTEM_NAME})
    outfile = 'war-in-the-north-hero-revive-triggers.txt'
    with open(outfile, 'w') as f:
        f.write(revive_system)

