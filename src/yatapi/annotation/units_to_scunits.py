"""

"""

from yatapi.annotation.generate_triggers_api import  _argument_to_constant_name


# ALAN_SCHEZAR_GOLIATH = SCUnit('"Alan Schezar (Goliath)"')
def unit_to_scunit(unit):
    """

    Input: 'Alan Schezar (Goliath)'
    Output: ALAN_SCHEZAR_GOLIATH = SCUnit('"Alan Schezar (Goliath)"')

    :param unit:
    :type unit: str
    :return:
    """
    constname = _argument_to_constant_name(unit)
    unit = unit.replace("'", "\\'")
    return '{} = SCUnit(\'"{}"\')'.format(constname, unit)


def generate_from_units(units, outfile):
    lines = '\n'.join([unit_to_scunit(x) for x in units])
    with open(outfile, 'w') as f:
        f.write(lines)


if __name__ == '__main__':
    with open('data/trigedit-units.txt', 'r') as f:
        units = f.read().split('\n')
    units = sorted(units)
    generate_from_units(units, 'trigedit_units.py')
