"""Wrapper for a Starcraft trigger that contains players, conditions, and actions.

"""

import json
import re
import typing

import yatapi.logger
import yatapi.scplayer
import yatapi.trigger_statements

WIN_NEWLINE = '\r\n'
NIX_NEWLINE = '\n'

# used by SCMDraft TrigEdit to separate each trigger
TRIGGER_SEPARATOR = '//-----------------------------------------------------------------//'
TRIGGER_START = '{'
TRIGGER_END = '}'
TRIGGER_ACTION = 'action'
TRIGGER_CONDITION = 'condition'

# regular expressions to parse TrigEdit format
PLAYERS_RE = re.compile(r'Trigger\((?P<players>[^\)]+?)\){', re.IGNORECASE)
CONDITIONS_RE = re.compile(r'Conditions:(?P<conditions>.+?)Actions:', re.IGNORECASE | re.DOTALL)
ACTIONS_RE = re.compile(r'Actions:(?P<actions>.+)', re.IGNORECASE | re.DOTALL)
STATEMENT_RE = re.compile(r'(?P<name>[^\(]+)\((?P<args>.*?)\)$', re.DOTALL)

# prefix/regex for indicating if comment is JSON data
JSON_COMMENT_PREFIX = 'JSON='
JSON_COMMENT_REGEX = re.compile(r'^"JSON=(?P<json>.+?)"\);$')


def parse_comma_separated_args(raw_args):
    """Parses an string of comma separated arguments into each argument.

    Ignores commas inside double quotes.
    Does not handle multiple double quotes or incorrectly nested double quotes.

    Input: 'Always Display, "Please wait for Player 1 to decide to enable or skip tutorial."'
    Output: ['Always Display', '"Please wait for Player 1 to decide to enable or skip tutorial."']

    :param raw_args:
    :type raw_args: str
    :return:
    """
    start = 0
    args = []
    curr_arg = ''
    inside_quote = False
    while start < len(raw_args):
        car = raw_args[start]
        if car == ',':
            if inside_quote:
                curr_arg += car
            else:
                args.append(curr_arg)
                curr_arg = ''
        elif car == '"':
            curr_arg += car
            if inside_quote:
                inside_quote = False
            else:
                inside_quote = True
        else:
            curr_arg += car
        start += 1
    if curr_arg != '':
        args.append(curr_arg)
    return args


class TrigEditParser:
    def __init__(self):
        self.log = yatapi.logger.get_log(TrigEditParser.__name__)

    def _get_trigger_blocks(self, text):
        """Gets each trigger block from the text, as separated by `TRIGGER_SEPARATOR`.

        :return:
        :param text: text contained TrigEdit triggers separated by `TRIGGER_SEPARATOR`.
        """
        return text.split(TRIGGER_SEPARATOR)

    def parse_trigger(self, text):
        """Parses an SCMDraft TrigEdit text based trigger into players, conditions, and actions.

        :param text:
        :return: a dictionary with players, conditions, and actions keys
        :rtype: dict
        """
        pm = PLAYERS_RE.search(text)
        if not pm:
            self.log.error('Unable to extract players from trigger: {}'.format(text))
        players = pm.group('players')
        conds_match = CONDITIONS_RE.search(text)
        if not conds_match:
            self.log.error('Unable to extract conditions from trigger: {}'.format(text))
        raw_conditions = conds_match.group('conditions')
        conditions = [x.strip() for x in raw_conditions.split(';')]
        conditions = [x for x in conditions if x]
        actions_match = ACTIONS_RE.search(text)
        if not actions_match:
            self.log.error('Unable to extract actions from trigger: {}'.format(text))
        raw_actions = actions_match.group('actions')
        actions = [x.strip() for x in raw_actions.split(';')]
        actions = [x for x in actions if x]
        # filter end brace to allow JSON in Comment actions
        actions = [x for x in actions if x != '}']
        return {'players': players, 'conditions': conditions, 'actions': actions}

    def extract_triggers(self, text):
        blocks = self._get_trigger_blocks(text)
        for block in blocks:
            block = block.strip()
            if block:
                yield self.parse_trigger(block)

    def extract_triggers_from_file(self, infile):
        with open(infile, 'r') as f:
            text = f.read()
        return self.extract_triggers(text)

    def parse_statement(self, text, statement_type=None):
        """Parses a statement (condition or action) into its name (e.g. "Kills") and arguments.

        Input: 'Deaths("Current Player", "Protoss Observer", At least, 1)'
        Output: {'name': 'Deaths', 'args': ['"Current Player"', '"Protoss Observer"', 'At least', 1]}

        Input: 'Always()'
        Output: {'name': 'Always', 'args': []}

        :param text:
        :param statement_type: whether the statement is a trigger action or condition.
        :return:
        """
        match = STATEMENT_RE.search(text)
        if not match:
            self.log.error('Unable to parse this trigger statement: {}'.format(text))
        name = match.group('name')
        raw_args = match.group('args')
        args = parse_comma_separated_args(raw_args)
        args = [x.strip() for x in args]
        out = {'name': name, 'args': args}
        if statement_type:
            out['type'] = statement_type
        return out


def parse_trigedit_trigs_into_text():
    with open('data/compiled-triggers/demon-lore-triggers-2019-02-7.txt', 'r') as f:
        t = f.read()
    parser = TrigEditParser()
    trigs = parser.extract_triggers(t)
    acts = set()
    raws = []
    for x in trigs:
        for c in x['conditions']:
            z = parser.parse_statement(c)
        for c in x['actions']:
            a = parser.parse_statement(c)
            acts.add(json.dumps(a))
            raws.append(c)
    acts = list(acts)
    acts.sort()
    for x in acts:
        x = json.loads(x)
        num_args = len(x['args'])
        print(num_args, x)


class Trigger:
    def __init__(self, players: typing.List[yatapi.scplayer.SCPlayer],
                 conditions: typing.List[yatapi.trigger_statements.Condition],
                 actions: typing.List[yatapi.trigger_statements.Action]):
        """Instantiate a trigger with its players, conditions, and actions.

        :param players:
        :param conditions:
        :param actions:
        """
        self.players = players
        self.conditions = conditions
        self.actions = actions

    def add_action(self, action):
        self.actions.append(action)

    def compile(self, newline: str = WIN_NEWLINE) -> str:
        """Generates SCMDraft TrigEdit text based representation of the trigger.

        :param newline: whether to use Windows or *Nix newline endings;
                        default is Windows: '\r\n'
        :type newline: str
        :return: SCMDraft TrigEdit text representation of the trigger
        :rtype: str
        """
        raw_players = ','.join([str(x) for x in self.players])
        trig = 'Trigger({}){{'.format(raw_players)
        conds = '\n\t'.join([x.compile() for x in self.conditions])
        trig += '\nConditions:\n\t{}\n'.format(conds)
        actions = '\n\t'.join([x.compile() for x in self.actions])
        trig += '\nActions:\n\t{}\n\n'.format(actions)
        trig += '}\n\n'
        trig += TRIGGER_SEPARATOR
        # use Windows newline endings if applicable
        trig = trig.replace('\n', newline)
        return trig

    def __repr__(self):
        return self.compile()


def compile_triggers(triggers: typing.List[Trigger], jsondata: typing.Optional[typing.Dict]=None, newline: str=WIN_NEWLINE):
    """Compiles a set of triggers ready for copy into SCMDraft.

    :param triggers: list of Triggers ready to be compiled to TrigEdit format
    :param jsondata: arbitrary JSON data to be placed in a comment
                     added to each trigger.  Very useful to keep track of trigger systems in
                     larger maps.
    :param newline: which newline to use; default will use Windows newlines
    :return: TrigEdit triggers ready to be copied into SCMDraft
    """
    # add in json comment if needed
    if jsondata:
        safe_json = json.dumps(jsondata).replace('"', '\'')
        comment = yatapi.trigger_statements.Comment(JSON_COMMENT_PREFIX + safe_json)
        for trigger in triggers:
            trigger.add_action(comment)
    return (newline * 2).join([x.compile(newline=newline) for x in triggers])


if __name__ == '__main__':
    infile = '../../data/war-in-the-north-revive-all-triggers.txt'
    parser = TrigEditParser()
    t = list(parser.extract_triggers_from_file(infile))
    print(json.dumps(t[0], indent=1))
    z = Trigger([1], [2], [3])
    # from trigger_statements import *
    # from scscript import *
    # players = [SCPlayer('"Player 1"')]
    # conditions = [Always()]
    # actions = [RunAiScript(script=VI7)]
    # t = Trigger(players, conditions, actions)
    # z = t.compile()
    # print(z)

