#! /usr/bin/env python3
# pylint: disable=R0902
"""Simple character sheet backend for VtM."""
from copy import deepcopy
from datetime import datetime
import json


class Character:
    """Simple CtM character sheet."""
    def __init__(self):
        self.experience = {
            'current': 30,
            'total': 30,
            'log': [],
        }
        self.player = ''
        self.character = ''
        self.archetype = ''
        self.clan = ''
        self.sect = ''
        self.title = ''
        self.attributes = {
            'physical': {
                'value': 0,
                'focuses': [],
            },
            'social': {
                'value': 0,
                'focuses': [],
            },
            'mental': {
                'value': 0,
                'focuses': [],
            },
        }
        self.skills = {}
        self.backgrounds = {}
        self.disciplines = {}
        self.merits = {}
        self.flaws = {}
        self.derangements = []
        self.blood = {
            'max': 0,
            'current': 0,
            'rate': 0,
        }
        self.willpower = {
            'max': 6,
            'current': 6,
        }
        self.morality = {
            'max': 5,
            'current': 5,
            'beast traits': 0,
        }
        self.health_levels = {
            'healthy': 3,
            'injured': 3,
            'incapacitated': 3,
        }
        self.damage_taken = []
        self.notes = []
        self.status = []
        self.equipment = []

    def award_xp(self, amount, reason):
        """Award XP to this character."""
        self.experience['current'] += amount
        self.experience['total'] += amount
        self.experience['log'].append('{}- Gained {} ({})'.format(
            datetime.now().strftime('%Y/%m/%d %H:%M'),
            amount,
            reason,
        ))

    def spend_xp(self, amount, reason):
        """Indicate XP has been spent on this character, and what for."""
        self.experience['current'] -= amount
        self.experience['log'].append('{}- Spent {} ({})'.format(
            datetime.now().strftime('%Y/%m/%d %H:%M'),
            amount,
            reason,
        ))

    def get_health_level(self):
        """Return the character's current health level."""
        health = []
        for level in [
                'healthy', 'injured', 'incapacitated'
        ]:
            health.extend([level for i in range(self.health_levels[level])])
        if len(self.damage_taken) <= len(health):
            pos = max(len(self.damage_taken) - 1, 0)
            return health[pos]
        return 'torpid'

    def get_xp_costs(self):
        """Return a dict of XP costs for this character."""
        if all(gen in self.backgrounds for gen in
               ('generation', 'Generation')):
            raise RuntimeError('Generation set multiple times.')
        generation = (
            self.backgrounds.get('generation')
            or self.backgrounds.get('Generation', 1)
        )

        xp_costs = {
            'Attribute': 3,
            'In-clan discipline': 'new level x 3',
            'Regain lost humanity': 10,
            'Merit': 'rating',
            'Ritual': 'rating x 2',
            'Background': 'new level x 2',
            'Skill': 'new level x 2',
            'Out-of-clan discipline': 'new level x 4',
            'Technique': 12,
            'In-clan elder power': 'Not allowed',
            'Out-of-clan elder power': 'Not allowed',
        }

        if generation == 1:
            xp_costs['Background'] = 'new level x 1'
            xp_costs['Skill'] = 'new level x 1'
        elif generation == 3:
            xp_costs['Technique'] = 20
            xp_costs['In-clan elder power'] = (
                '(max one in/out-of-clan elder power) 18'
            )
            xp_costs['Out-of-clan elder power'] = (
                '(max one in/out-of-clan elder power) 24'
            )
        elif generation == 4:
            xp_costs['Technique'] = 'Not allowed'
            xp_costs['In-clan elder power'] = 18
            xp_costs['Out-of-clan elder power'] = 24
        elif generation == 5:
            xp_costs['Technique'] = 'Not allowed'
            xp_costs['In-clan elder power'] = 18
            xp_costs['Out-of-clan elder power'] = 30
            xp_costs['Out-of-clan discipline'] = 'new level x 5'

        return xp_costs

    def to_json(self):
        """Return a json dump of the character."""
        return json.dumps({
            'header': {
                'player': self.player,
                'character': self.character,
                'archetype': self.archetype,
                'clan': self.clan,
                'sect': self.sect,
                'title': self.title,
            },
            'xp': self.experience,
            'attributes': self.attributes,
            'skills': self.skills,
            'backgrounds': self.backgrounds,
            'disciplines': self.disciplines,
            'merits_and_flaws': {
                'merits': self.merits,
                'flaws': self.flaws,
                'derangements': self.derangements,
            },
            'state': {
                'blood': self.blood,
                'willpower': self.willpower,
                'morality': self.morality,
                'health': {
                    'levels': self.health_levels,
                    'damage': self.damage_taken,
                },
                'status': self.status,
            },
            'equipment': self.equipment,
            'notes': self.notes,
        }, sort_keys=True)

    def from_json(self, json_data):
        """Load this character from a json dump."""
        data = json.loads(json_data)

        header = data['header']
        self.player = header['player']
        self.character = header['character']
        self.archetype = header['archetype']
        self.clan = header['clan']
        self.sect = header['sect']
        self.title = header['title']

        merits_and_flaws = data['merits_and_flaws']
        self.merits = merits_and_flaws['merits']
        self.flaws = merits_and_flaws['flaws']
        self.derangements = merits_and_flaws['derangements']

        state = data['state']
        self.blood = state['blood']
        self.willpower = state['willpower']
        self.morality = state['morality']
        self.health_levels = state['health']['levels']
        self.damage_taken = state['health']['damage']

        self.experience = data['xp']
        self.attributes = data['attributes']
        self.skills = data['skills']
        self.backgrounds = data['backgrounds']
        self.disciplines = data['disciplines']
        self.equipment = data['equipment']
        self.notes = data['notes']


_BASE_EXPECTED = {
    'header': {
        'player': '',
        'character': '',
        'archetype': '',
        'clan': '',
        'sect': '',
        'title': '',
    },
    'xp': {
        'current': 30,
        'total': 30,
        'log': [],
    },
    'attributes': {
        'physical': {
            'value': 0,
            'focuses': [],
        },
        'social': {
            'value': 0,
            'focuses': [],
        },
        'mental': {
            'value': 0,
            'focuses': [],
        },
    },
    'skills': {},
    'backgrounds': {},
    'disciplines': {},
    'merits_and_flaws': {
        'merits': {},
        'flaws': {},
        'derangements': [],
    },
    'state': {
        'blood': {
            'current': 0,
            'max': 0,
            'rate': 0,
        },
        'willpower': {
            'current': 6,
            'max': 6,
        },
        'morality': {
            'max': 5,
            'current': 5,
            'beast traits': 0,
        },
        'health': {
            'levels': {
                'healthy': 3,
                'injured': 3,
                'incapacitated': 3,
            },
            'damage': [],
        },
        'status': [],
    },
    'equipment': [],
    'notes': [],
}


def _assert_expected_character(character, expected):
    header = expected['header']
    assert character.player == header['player']
    assert character.character == header['character']
    assert character.archetype == header['archetype']
    assert character.clan == header['clan']
    assert character.sect == header['sect']
    assert character.title == header['title']

    merits_and_flaws = expected['merits_and_flaws']
    assert character.merits == merits_and_flaws['merits']
    assert character.flaws == merits_and_flaws['flaws']
    assert character.derangements == merits_and_flaws['derangements']

    state = expected['state']
    assert character.blood == state['blood']
    assert character.willpower == state['willpower']
    assert character.morality == state['morality']
    assert character.health_levels == state['health']['levels']
    assert character.damage_taken == state['health']['damage']

    assert character.experience == expected['xp']
    assert character.attributes == expected['attributes']
    assert character.skills == expected['skills']
    assert character.backgrounds == expected['backgrounds']
    assert character.disciplines == expected['disciplines']
    assert character.equipment == expected['equipment']
    assert character.notes == expected['notes']


def _test_initial_character():
    print('Checking base character...', end='')
    char = Character()
    _assert_expected_character(char, _BASE_EXPECTED)
    print(' OK.')


def _test_dump():
    print('Checking json dump...', end='')
    char = Character()
    dump = char.to_json()
    assert dump == json.dumps(_BASE_EXPECTED, sort_keys=True)
    print(' OK.')
    print('Checking json dump with updated char...', end='')
    char.character = 'Alucard'
    expected = deepcopy(_BASE_EXPECTED)
    expected['header']['character'] = 'Alucard'
    dump = char.to_json()
    assert dump == json.dumps(expected, sort_keys=True)
    print(' OK.')


def _test_load():
    print('Checking json load...', end='')
    char = Character()
    new = deepcopy(_BASE_EXPECTED)
    new['disciplines']['sneakiness'] = 4
    new['state']['damager'] = 255
    char.from_json(json.dumps(new))
    _assert_expected_character(char, new)
    print(' OK.')


def _test_get_health_level():
    print('Checking health levels...', end='')
    char = Character()
    assert char.get_health_level() == 'healthy'
    char.damage_taken = ['normal', 'normal', 'aggravated']
    assert char.get_health_level() == 'healthy'
    char.damage_taken.append('aggravated')
    assert char.get_health_level() == 'injured'
    char.damage_taken.extend(['normal', 'normal'])
    assert char.get_health_level() == 'injured'
    char.damage_taken.append('normal')
    assert char.get_health_level() == 'incapacitated'
    char.damage_taken.extend(['normal', 'aggravated'])
    assert char.get_health_level() == 'incapacitated'
    char.damage_taken.append('normal')
    assert char.get_health_level() == 'torpid'
    print(' OK.')


def _test_xp_costs():
    print('Checking XP cost listing...', end='')
    exp = {
        'Attribute': 3,
        'In-clan discipline': 'new level x 3',
        'Regain lost humanity': 10,
        'Merit': 'rating',
        'Ritual': 'rating x 2',
        'Background': 'new level x 1',
        'Skill': 'new level x 1',
        'Out-of-clan discipline': 'new level x 4',
        'Technique': 12,
        'In-clan elder power': 'Not allowed',
        'Out-of-clan elder power': 'Not allowed',
    }
    char = Character()

    char.backgrounds['Generation'] = 1
    assert char.get_xp_costs() == exp

    char.backgrounds.pop('Generation')
    char.backgrounds['generation'] = 2
    exp['Background'] = 'new level x 2'
    exp['Skill'] = 'new level x 2'
    assert char.get_xp_costs() == exp

    char.backgrounds.pop('generation')
    char.backgrounds['Generation'] = 3
    exp['Technique'] = 20
    exp['In-clan elder power'] = '(max one in/out-of-clan elder power) 18'
    exp['Out-of-clan elder power'] = '(max one in/out-of-clan elder power) 24'
    assert char.get_xp_costs() == exp

    char.backgrounds.pop('Generation')
    char.backgrounds['generation'] = 4
    exp['Technique'] = 'Not allowed'
    exp['In-clan elder power'] = 18
    exp['Out-of-clan elder power'] = 24
    assert char.get_xp_costs() == exp

    char.backgrounds.pop('generation')
    char.backgrounds['Generation'] = 5
    exp['Out-of-clan elder power'] = 30
    exp['Out-of-clan discipline'] = 'new level x 5'
    assert char.get_xp_costs() == exp

    char.backgrounds['generation'] = 4
    try:
        char.get_xp_costs()
        assert False
    except RuntimeError as err:
        assert 'Generation set multiple times.' in str(err)
    print(' OK.')


def _test_xp():
    print('Checking award XP...', end='')
    char = Character()
    char.award_xp(4, 'for testing')
    assert char.experience['current'] == 34
    assert char.experience['total'] == 34
    assert len(char.experience['log']) == 1
    message = char.experience['log'][0].split('-', 1)[1]
    assert message == ' Gained 4 (for testing)'

    char.spend_xp(3, 'increase mental attribute')
    assert char.experience['current'] == 31
    assert char.experience['total'] == 34
    assert len(char.experience['log']) == 2
    message = char.experience['log'][1].split('-', 1)[1]
    assert message == ' Spent 3 (increase mental attribute)'
    print(' OK.')


if __name__ == '__main__':
    _test_initial_character()
    _test_dump()
    _test_load()
    _test_get_health_level()
    _test_xp_costs()
    _test_xp()
