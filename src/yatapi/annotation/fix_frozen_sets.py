"""

"""

import re

# frozenset(["player, unit, location"])
FROZEN_RE = re.compile(r'frozenset\(\["(?P<values>[^"]+)"\]\)')


def new_frozenset(raw_values):
    vals = raw_values.split(', ')
    new_vals = ['"{}"'.format(x) for x in vals]
    return ', '.join(new_vals)


def fix_frozensets(raw):
    all_matches = [x for x in FROZEN_RE.finditer(raw)]
    for match in all_matches:
        original = match.group()
        vals = match.group('values')
        if vals:
            new = 'frozenset([{}])'.format(new_frozenset(vals))
            raw = raw.replace(original, new)
    raw = raw.replace('frozenset([""])', 'frozenset()')
    return raw



if __name__ == '__main__':
    infile = 'trigger_statements.py'
    with open(infile, 'r') as f:
        raw = f.read()
    n = fix_frozensets(raw)
    with open(infile, 'w') as f:
        f.write(n)
    # matches = FROZEN_RE.findall(raw)
    # print(matches)
    # z = new_frozenset(matches[1])
