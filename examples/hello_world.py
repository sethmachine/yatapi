"""Hello World Demo.

"""

from yatapi.scplayer import ALL_PLAYERS, CURRENT_PLAYER
from yatapi.scquantifier import EXACTLY
import yatapi.scunit
import yatapi.trigger
from yatapi.trigger_statements import *

conditions = [Command(CURRENT_PLAYER, yatapi.scunit.TERRAN_MARINE, EXACTLY, 1)]
actions = [DisplayTextMessage('Hello World!')]
trigger = yatapi.trigger.Trigger([ALL_PLAYERS], conditions, actions)
print(trigger.compile())