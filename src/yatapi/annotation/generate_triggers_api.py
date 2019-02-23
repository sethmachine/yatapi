"""Interactive utility to parse text trigger actions and conditions into signatures to build a Python triggers API.

"""

import collections
import json
import os
import re
import shutil
from string import punctuation
from typing import List, Union

import yatapi.trigger

CONDITION = 'condition'
ACTION = 'action'

TABSIZE = 4


class Annotator:
    def __init__(self, outdir, redo=False):
        """Annotate condition and action signatures to create data for a Python Trigger API.

        :param outdir:
        """
        self.outdir = outdir
        if redo:
            shutil.rmtree(outdir)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        self.annotations_file = os.path.join(outdir, 'annotations.json')
        self.annotations = collections.defaultdict(dict)
        if os.path.exists(self.annotations_file):
            annotations = json.load(open(self.annotations_file, 'r'))
            for key1 in annotations:
                for key2 in annotations[key1]:
                    self.annotations[key1][key2] = annotations[key1][key2]
        self.argtypes = {}
        self.argtypes_file = os.path.join(outdir, 'argtypes.json')
        if os.path.exists(self.argtypes_file):
            self.argtypes = json.load(open(self.argtypes_file, 'r'))

    def annotate_file(self, infile):
        """Annotates signatures from a file containing blocks of SCMDraft TrigEdit triggers.

        :param infile: plain text file with SCMDraft TrigEdit triggers
        :type infile: str
        :return:
        """
        with open(infile, 'r') as f:
            raw = f.read()
        parser = yatapi.trigger.TrigEditParser()
        trigs = parser.extract_triggers(raw)
        for trig in trigs:
            for condition in trig['conditions']:
                self._annotate_statement(parser.parse_statement(condition), CONDITION)
            for action in trig['actions']:
                self._annotate_statement(parser.parse_statement(action), ACTION)

    def _annotate_statement(self, statement, statement_type):
        """

        :param statement: dictionary with "name" and "args" keys
        :param statement_type: whether it is a condition or action
        :return:
        """
        is_annotated = self.annotations[statement_type].get(statement['name'])
        print('Annotating: {}'.format(json.dumps(statement)))
        annotated_args = []
        for i, arg in enumerate(statement['args']):
            if is_annotated:
                argtype = self.annotations[statement_type][statement['name']][i]['type']
            elif arg in self.argtypes:
                argtype = self.argtypes[arg]
                print('Skipping {} because associated with type {}'.format(arg, argtype))
            else:
                print('What is the type of arg #{}: {}\n'.format(i, arg))
                argtype = input()
                print('Arg {} is type {}'.format(arg, argtype))
            is_quoted = True if '"' in arg else False
            new_arg = {'type': argtype, 'position': i, 'is_quoted': is_quoted,
                       'default': arg}
            annotated_args.append(new_arg)
            self.argtypes[arg] = argtype
        self.annotations[statement_type][statement['name']] = annotated_args
        json.dump(self.annotations, open(self.annotations_file, 'w'), indent=1)
        json.dump(self.argtypes, open(self.argtypes_file, 'w'), indent=1)


def type_to_sc_type(type_, prefix='sc'):
    """Generates the classname used for the Starcraft argument type.

    :param type_:
    :return:
    """
    return '{}{}'.format(prefix.upper(), type_.title())


def generate_python_trigger_api(annotations, template, sctypes, outfile):
    with open(template, 'r') as f:
        raw_template = f.read()
    all_imports = []
    classes_ = []
    for type_ in annotations:
        annot_names = sorted(list(annotations[type_].keys()))
        for annot in annot_names:
            args = annotations[type_][annot]
            cls, imports = annotation_to_python(annot, args, type_, raw_template, sctypes)
            all_imports += imports
            classes_.append(cls)
    all_imports = sorted(set(all_imports))
    raw_imports = generate_trigger_api_imports(all_imports)
    all_classes = '\n\n'.join(classes_)
    # add in imports
    raw_template = raw_template.replace('# BEGIN imports', raw_imports)
    # add in classes
    raw_template = raw_template.replace('# BEGIN ACTIONS', all_classes)
    with open(outfile, 'w') as f:
        f.write(raw_template)


def annotation_to_python(name, args, type_, template, sctypes):
    """Turns a JSON annotation into a Python object.

    :param name: name of the trigger action or condition
    :param args: arguments of the trigger action or condition in JSON
    :param type_: whether it is an action or condition
    :return:
    """
    tab = ' ' * TABSIZE
    tokens = name.split(' ')
    pyname = ''.join([x.title() for x in tokens])
    cls = 'class {}({}):\n'.format(pyname, type_.title())
    cls += '{}_trigedit_name = "{}"\n'.format(tab, name)
    # pyargs = [type_to_sc_type(x['type']) for x in args]
    qparams = [x['type'] for x in args if x['is_quoted']]
    quoted_fields = '["{}"]'.format(', '.join(qparams))
    if not quoted_fields:
        quoted_fields = ''
    cls += '{}_quoted_fields = frozenset({})\n\n'.format(tab, quoted_fields)
    # figure out the argument types
    imports = []
    for arg in args:
        param = arg['type']
        default = arg['default']
        if param in sctypes:
            ptype = type_to_sc_type(param, prefix='sc')
            imports.append(ptype)
        else:
            if re.search('^[0-9]+$', default):
                ptype = 'int'
            else:
                ptype = 'str'
        arg['pytype'] = ptype
    if len(args) > 0:
        typed_params = ', '.join(['{}: {}'.format(x['type'], x['pytype']) for x in args])
        cls += '{}def __init__(self, {}):\n'.format(tab, typed_params)
    else:
        cls += '{}def __init__(self):\n'.format(tab)
    joiner = '\n{}{}'.format(tab, tab)
    fields = joiner.join(['self.{} = {}'.format(x['type'], x['type']) for x in args])
    if len(args) > 0:
        cls += '{}{}super().__init__()\n{}{}{}'.format(tab, tab, tab, tab, fields)
    else:
        cls += '{}{}super().__init__()'.format(tab, tab)
    return cls, imports

def generate_trigger_api_imports(imports):
    return '\n'.join(['from {} import {}'.format(x.lower(), x) for x in imports])

def generate_python_argument_types(argtypes: Union[List, str], outdir: str, prefix: str = 'sc', types=None):
    """Generates Python classes for each argument type and list of known constants.

    :param argtypes:
    :param outdir:
    :param prefix:
    :return:
    """
    if type(argtypes) is str:
        argtypes = json.load(open(argtypes, 'r'))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    type_to_args = collections.defaultdict(set)
    for arg in argtypes:
        argtype = argtypes[arg]
        if types is not None:
            if argtype not in types:
                continue
        type_to_args[argtype].add(arg)
    for argtype in type_to_args:
        real_args = sorted(list(type_to_args[argtype]))
        arguments_to_python(real_args, argtype, outdir, prefix)


def _argument_to_constant_name(arg):
    # only digits not valid python var name
    if re.search(r'^[0-9\.]+$', arg):
        arg = arg.replace('.', '_')
        return 'DIGITS_{}'.format(arg)
    arg = ''.join([car for car in arg if car not in punctuation])
    arg = arg.replace(' ', '_')
    return arg.upper()


def arguments_to_python(arguments, argtype, outdir, prefix):
    """

    :param arguments:
    :param argtype:
    :return:
    """
    outfile = os.path.join(outdir, '{}{}.py'.format(prefix, argtype.lower()))
    classname = type_to_sc_type(argtype, prefix)
    tab = ' ' * TABSIZE
    # generate the top doc string
    body = '"""Wrapper for a Starcraft {} reference.\n\n"""'.format(argtype.title())
    body += '\n\n\n'
    # generate the actual wrapper
    body += 'class {}:\n\tdef __init__(self, value: str):\n'.format(classname)
    body += '\t\tself.value = value\n\n'
    body += '\tdef __repr__(self):\n\t\treturn self.value\n\n\n'
    # generate constants
    used_arguments = set()
    for arg in arguments:
        constant_name = _argument_to_constant_name(arg)
        if constant_name in used_arguments:
            continue
        used_arguments.add(constant_name)
        # escape any single quotes
        arg = arg.replace("'", "\\'")
        line = '{} = {}(\'{}\')\n'.format(constant_name, classname, arg)
        body += line
    body = body.replace('\t', tab)
    with open(outfile, 'w') as f:
        f.write(body)


def create_argtype_python_classes():
    argtypes = 'data/trigger-annotations-2/argtypes.json'
    types = json.load(open('data/sc-types.json', 'r'))
    generate_python_argument_types(argtypes, outdir='data/generated-trigger-pyfiles-2', types=types)


if __name__ == '__main__':
    # infile = 'data/compiled-triggers/demon-lore-triggers-2019-02-7.txt'
    # annotator = Annotator('data/trigger-annotations-2', redo=False)
    # annotator.annotate_file(infile)
    infile = json.load(open('data/trigger-annotations-2/annotations.json', 'r'))
    sctypes = json.load(open('data/sc-types.json'))
    template = 'data/templates/trigger_statement_real_template.py'
    generate_python_trigger_api(infile, template, sctypes, 'trigger_statements.py')



