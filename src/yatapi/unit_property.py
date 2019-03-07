"""Represents a unit property that can be used in a trigger.

See: http://www.staredit.net/topic/17764/

Example:

Unit Property 0

HP:	100
SP:	100
EP:	100
Res:	0
Hangar Units:	0
Flags:	CLOAKED BURROWED INTRANSIT HALLUCINATED INVINCIBLE

"""

import json
import typing

from .trigger import WIN_NEWLINE, NIX_NEWLINE

CLOAKED = 'CLOAKED'
BURROWED = 'BURROWED'
LIFTED = 'INTRANSIT'
HALLUCINATED = 'HALLUCINATED'
INVINCIBLE = 'INVINCIBLE'


class UnitProperty:
    def __init__(self, hitpoints: int = 100, shields: int = 100, energy: int = 100,
                 resources: int = 0, hangar: int = 0, flags: typing.Union[typing.List[str], None] = None):
        self.hitpoints = hitpoints
        self.shields = shields
        self.energy = energy
        self.resources = resources
        self.hangar = hangar
        self.flags = flags
        if not self.flags:
            self.flags = []

    def compile(self, index=0, newline=WIN_NEWLINE) -> str:
        """Create the TrigEdit unit property.

        Unit Property 0

        HP:	100
        SP:	100
        EP:	100
        Res:	0
        Hangar Units:	0
        Flags:	CLOAKED BURROWED INTRANSIT HALLUCINATED INVINCIBLE

        :param index:
        :type index: int
        :return:
        """
        flags = ' '.join(self.flags)
        out = 'Unit Property {}\nHP: {}\nSP: {}\nEP: {}\nRes: {}\nHangar Units: {}\nFlags: {}\n'.format(
            index, self.hitpoints, self.shields, self.energy, self.resources, self.hangar, flags)
        return out.replace('\n', newline)

    def __repr__(self):
        return json.dumps(vars(self))


def compile_properties(properties: typing.List[UnitProperty], newline=WIN_NEWLINE) -> str:
    """Must always be 64 properties, will make default ones if not 64 passed.

    :param properties:
    :return:
    """
    out = []
    for i, prop in enumerate(properties):
        out.append(prop.compile(index=i, newline=newline))
    for x in range(i + 1, 64):
        out.append(UnitProperty().compile(index=x, newline=newline))
    return newline.join(out)



if __name__ == '__main__':
    up = UnitProperty(hitpoints=80, flags=[CLOAKED])
    print(up)
    print(up.compile())
    o = up.compile()
    z = compile_properties([up, up])
    print(z)
    outfile = '/Volumes/Users/sdwor/OneDrive/Desktop/props.txt'
    with open(outfile, 'w') as f:
        f.write(z)
