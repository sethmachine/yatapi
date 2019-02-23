"""

"""

import abc
import inspect
import re

# module level imports go here
from scaction import SCAction
from scalliance import SCAlliance
from scoperation import SCOperation
from scorder import SCOrder
from scplayer import SCPlayer
from scquantifier import SCQuantifier
from scresource import SCResource
from scscript import SCScript
from scstate import SCState
from scunit import SCUnit
from scvisibility import SCVisibility, ALWAYS_DISPLAY


class Statement(abc.ABC):
    _trigedit_name = 'statement'
    _quoted_fields = frozenset()

    def __init__(self):
        pass

    def _is_quoted(self, value):
        return True if re.search(r'^".+?"$', value) is not None else False

    def _quote_value(self, value):
        return '"{}"'.format(value)

    def compile(self, pretty=False) -> str:
        """Compiles the action/condition into format usable by SCMDraft TrigEdit.

        :param pretty: whether to include name of each argument (cannot be used in TrigEdit); use for debugging
        :type pretty: bool
        :return: a string representing the TrigEdit format for the trigger action or condition
        :rtype: str
        """
        values = []
        for arg in inspect.getfullargspec(self.__init__).args:
            if arg != 'self':
                value = getattr(self, arg)
                if arg in self.__class__._quoted_fields and type(value) == str:
                    if not self._is_quoted(value):
                        value = self._quote_value(value)
                if pretty:
                    values.append('{}={}'.format(arg, value if type(value) == str else str(value)))
                else:
                    values.append(value if type(value) == str else str(value))
        return '{}({});'.format(self.__class__._trigedit_name, ', '.join(values))

    def __repr__(self):
        return self.compile()


class Condition(Statement):
    _trigedit_name = 'condition'

    def __init__(self):
        super().__init__()
        self.type = self.__class__.__name__


class Action(Statement):
    _trigedit_name = 'action'

    def __init__(self):
        super().__init__()
        self.type = self.__class__.__name__


# actions and conditions go here
class Accumulate(Condition):
    _trigedit_name = "Accumulate"
    _quoted_fields = frozenset(["player"])

    def __init__(self, player: SCPlayer, quantifier: SCQuantifier, amount: int, resource: SCResource):
        super().__init__()
        self.player = player
        self.quantifier = quantifier
        self.amount = amount
        self.resource = resource


class Always(Condition):
    _trigedit_name = "Always"
    _quoted_fields = frozenset()

    def __init__(self):
        super().__init__()


class Bring(Condition):
    _trigedit_name = "Bring"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, location: str, quantifier: SCQuantifier, count: int):
        super().__init__()
        self.player = player
        self.unit = unit
        self.location = location
        self.quantifier = quantifier
        self.count = count


class Command(Condition):
    _trigedit_name = "Command"
    _quoted_fields = frozenset(["player", "unit"])

    def __init__(self, player: SCPlayer, unit: SCUnit, quantifier: SCQuantifier, count: int):
        super().__init__()
        self.player = player
        self.unit = unit
        self.quantifier = quantifier
        self.count = count


class CountdownTimer(Condition):
    _trigedit_name = "Countdown Timer"
    _quoted_fields = frozenset()

    def __init__(self, quantifier: SCQuantifier, count: int):
        super().__init__()
        self.quantifier = quantifier
        self.count = count


class Deaths(Condition):
    _trigedit_name = "Deaths"
    _quoted_fields = frozenset(["player", "unit"])

    def __init__(self, player: SCPlayer, unit: SCUnit, quantifier: SCQuantifier, count: int):
        super().__init__()
        self.player = player
        self.unit = unit
        self.quantifier = quantifier
        self.count = count


class HighestScore(Condition):
    _trigedit_name = "Highest Score"
    _quoted_fields = frozenset()

    def __init__(self, score: str):
        super().__init__()
        self.score = score


class Never(Condition):
    _trigedit_name = "Never"
    _quoted_fields = frozenset()

    def __init__(self):
        super().__init__()


class Switch(Condition):
    _trigedit_name = "Switch"
    _quoted_fields = frozenset(["switch"])

    def __init__(self, switch: str, state: SCState):
        super().__init__()
        self.switch = switch
        self.state = state


class CenterView(Action):
    _trigedit_name = "Center View"
    _quoted_fields = frozenset(["location"])

    def __init__(self, location: str):
        super().__init__()
        self.location = location


class Comment(Action):
    _trigedit_name = "Comment"
    _quoted_fields = frozenset(["text"])

    def __init__(self, text: str):
        super().__init__()
        self.text = text


class CreateUnit(Action):
    _trigedit_name = "Create Unit"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, count: int, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.count = count
        self.location = location


class CreateUnitWithProperties(Action):
    _trigedit_name = "Create Unit with Properties"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, count: int, location: str, properties: int):
        super().__init__()
        self.player = player
        self.unit = unit
        self.count = count
        self.location = location
        self.properties = properties


class Defeat(Action):
    _trigedit_name = "Defeat"
    _quoted_fields = frozenset()

    def __init__(self):
        super().__init__()


class DisplayTextMessage(Action):
    _trigedit_name = "Display Text Message"
    _quoted_fields = frozenset(["text"])

    def __init__(self, visibility: SCVisibility=ALWAYS_DISPLAY, text: str=''):
        super().__init__()
        self.visibility = visibility
        self.text = text


class GiveUnitsToPlayer(Action):
    _trigedit_name = "Give Units to Player"
    _quoted_fields = frozenset(["from_player", "to_player", "unit", "location"])

    def __init__(self, from_player: SCPlayer, to_player: SCPlayer, unit: SCUnit, count: str, location: str):
        super().__init__()
        self.from_player = from_player
        self.to_player = to_player
        self.unit = unit
        self.count = count
        self.location = location


class KillUnit(Action):
    _trigedit_name = "Kill Unit"
    _quoted_fields = frozenset(["player", "unit"])

    def __init__(self, player: SCPlayer, unit: SCUnit):
        super().__init__()
        self.player = player
        self.unit = unit


class KillUnitAtLocation(Action):
    _trigedit_name = "Kill Unit At Location"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, count: str, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.count = count
        self.location = location


class LeaderBoardControl(Action):
    _trigedit_name = "Leader Board Control"
    _quoted_fields = frozenset(["title", "unit"])

    def __init__(self, title: str, unit: SCUnit):
        super().__init__()
        self.title = title
        self.unit = unit


class LeaderBoardKills(Action):
    _trigedit_name = "Leader Board Kills"
    _quoted_fields = frozenset(["title", "unit"])

    def __init__(self, title: str, unit: SCUnit):
        super().__init__()
        self.title = title
        self.unit = unit


class LeaderBoardPoints(Action):
    _trigedit_name = "Leader Board Points"
    _quoted_fields = frozenset(["title"])

    def __init__(self, title: str, score: str):
        super().__init__()
        self.title = title
        self.score = score


class LeaderboardComputerPlayers(Action):
    _trigedit_name = "Leaderboard Computer Players"
    _quoted_fields = frozenset()

    def __init__(self, state: SCState):
        super().__init__()
        self.state = state


class MinimapPing(Action):
    _trigedit_name = "Minimap Ping"
    _quoted_fields = frozenset(["location"])

    def __init__(self, location: str):
        super().__init__()
        self.location = location


class ModifyUnitEnergy(Action):
    _trigedit_name = "Modify Unit Energy"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, resource: SCResource, count: int, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.resource = resource
        self.count = count
        self.location = location


class ModifyUnitHangerCount(Action):
    _trigedit_name = "Modify Unit Hanger Count"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, percent: int, count: int, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.percent = percent
        self.count = count
        self.location = location


class ModifyUnitHitPoints(Action):
    _trigedit_name = "Modify Unit Hit Points"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, percent: int, count: int, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.percent = percent
        self.count = count
        self.location = location


class ModifyUnitShieldPoints(Action):
    _trigedit_name = "Modify Unit Shield Points"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, percent: int, count: int, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.percent = percent
        self.count = count
        self.location = location


class MoveLocation(Action):
    _trigedit_name = "Move Location"
    _quoted_fields = frozenset(["player", "unit", "unit_location", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, unit_location: str, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.unit_location = unit_location
        self.location = location


class MoveUnit(Action):
    _trigedit_name = "Move Unit"
    _quoted_fields = frozenset(["player", "unit", "from_location", "to_location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, count: str, from_location: str, to_location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.count = count
        self.from_location = from_location
        self.to_location = to_location


class Order(Action):
    _trigedit_name = "Order"
    _quoted_fields = frozenset(["player", "unit", "location1", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, location1: str, location: str, order: SCOrder):
        super().__init__()
        self.player = player
        self.unit = unit
        self.location1 = location1
        self.location = location
        self.order = order


class PlayWav(Action):
    _trigedit_name = "Play WAV"
    _quoted_fields = frozenset(["wav"])

    def __init__(self, wav: str, unknown_wav_arg: int):
        super().__init__()
        self.wav = wav
        self.unknown_wav_arg = unknown_wav_arg


class PreserveTrigger(Action):
    _trigedit_name = "Preserve Trigger"
    _quoted_fields = frozenset()

    def __init__(self):
        super().__init__()


class RemoveUnit(Action):
    _trigedit_name = "Remove Unit"
    _quoted_fields = frozenset(["player", "unit"])

    def __init__(self, player: SCPlayer, unit: SCUnit):
        super().__init__()
        self.player = player
        self.unit = unit


class RemoveUnitAtLocation(Action):
    _trigedit_name = "Remove Unit At Location"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, count: int, location: str):
        super().__init__()
        self.player = player
        self.unit = unit
        self.count = count
        self.location = location


class RunAiScript(Action):
    _trigedit_name = "Run AI Script"
    _quoted_fields = frozenset(["script"])

    def __init__(self, script: SCScript):
        super().__init__()
        self.script = script


class RunAiScriptAtLocation(Action):
    _trigedit_name = "Run AI Script At Location"
    _quoted_fields = frozenset(["script", "location"])

    def __init__(self, script: SCScript, location: str):
        super().__init__()
        self.script = script
        self.location = location


class SetAllianceStatus(Action):
    _trigedit_name = "Set Alliance Status"
    _quoted_fields = frozenset(["player"])

    def __init__(self, player: SCPlayer, alliance: SCAlliance):
        super().__init__()
        self.player = player
        self.alliance = alliance


class SetCountdownTimer(Action):
    _trigedit_name = "Set Countdown Timer"
    _quoted_fields = frozenset()

    def __init__(self, operation: SCOperation, seconds: int):
        super().__init__()
        self.operation = operation
        self.seconds = seconds


class SetDeaths(Action):
    _trigedit_name = "Set Deaths"
    _quoted_fields = frozenset(["player", "unit"])

    def __init__(self, player: SCPlayer, unit: SCUnit, operation: SCOperation, count: int):
        super().__init__()
        self.player = player
        self.unit = unit
        self.operation = operation
        self.count = count


class SetDoodadState(Action):
    _trigedit_name = "Set Doodad State"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, location: str, state: SCState):
        super().__init__()
        self.player = player
        self.unit = unit
        self.location = location
        self.state = state


class SetInvincibility(Action):
    _trigedit_name = "Set Invincibility"
    _quoted_fields = frozenset(["player", "unit", "location"])

    def __init__(self, player: SCPlayer, unit: SCUnit, location: str, state: SCState):
        super().__init__()
        self.player = player
        self.unit = unit
        self.location = location
        self.state = state


class SetMissionObjectives(Action):
    _trigedit_name = "Set Mission Objectives"
    _quoted_fields = frozenset(["text"])

    def __init__(self, text: str):
        super().__init__()
        self.text = text


class SetResources(Action):
    _trigedit_name = "Set Resources"
    _quoted_fields = frozenset(["player"])

    def __init__(self, player: SCPlayer, operation: SCOperation, amount: int, resource: SCResource):
        super().__init__()
        self.player = player
        self.operation = operation
        self.amount = amount
        self.resource = resource


class SetScore(Action):
    _trigedit_name = "Set Score"
    _quoted_fields = frozenset(["player"])

    def __init__(self, player: SCPlayer, operation: SCOperation, count: int, score: str):
        super().__init__()
        self.player = player
        self.operation = operation
        self.count = count
        self.score = score


class SetSwitch(Action):
    _trigedit_name = "Set Switch"
    _quoted_fields = frozenset(["switch"])

    def __init__(self, switch: str, action: SCAction):
        super().__init__()
        self.switch = switch
        self.action = action


class Victory(Action):
    _trigedit_name = "Victory"
    _quoted_fields = frozenset()

    def __init__(self):
        super().__init__()


class Wait(Action):
    _trigedit_name = "Wait"
    _quoted_fields = frozenset()

    def __init__(self, milliseconds: int):
        super().__init__()
        self.milliseconds = milliseconds


if __name__ == '__main__':
    pass
