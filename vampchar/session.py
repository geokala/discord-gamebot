"""Session management for vampire sessions."""
from .sheet import Character


class BadInput(Exception):
    """Raised when bad input is supplied by the frontend."""


class Session: # pylint: disable=R0904
    """Vampire session manager."""
    player_characters = {}
    character_creation = True

    def load(self, session_save_path):
        """Load the game from its save path."""
        # TODO

    def save(self, session_save_path):
        """Save the game to its save path."""
        # TODO

    def add_player(self, player_id, player_name):
        """Add a player to the game."""
        if player_id in self.player_characters:
            raise BadInput("{} has already joined.".format(player_name))
        self.player_characters[player_id] = Character()
        self.player_characters[player_id].player = player_name
        return "Added {}.".format(player_name)

    def award_xp(self, amount, reason):
        """Award all players some XP for a given reason."""
        amount = self._check_int(amount)
        for character in self.player_characters.values():
            character.award_xp(amount, reason)
        return "All characters received {} XP for {}".format(
            amount, reason,
        )

    def get_player_json(self, player_id):
        """Get the json of a particular player's character sheet."""
        return self.player_characters[player_id].to_json()

    def add_focus(self, player_id, attribute, focus):
        """Add a focus on a given attribute."""
        if not self.character_creation:
            raise BadInput(
                "Focuses cannot be added after character creation.")
        self._validate_attribute(player_id, attribute)
        attributes = self.player_characters[player_id].attributes
        if focus in attributes[attribute]['focuses']:
            raise BadInput("You already have focus {} in attribute {}".format(
                focus, attribute,
            ))
        attributes[attribute]['focuses'].append(focus)
        return "Added {} to {} focuses.".format(focus, attribute)

    def remove_focus(self, player_id, attribute, focus):
        """Remove a focus from a given attribute."""
        if not self.character_creation:
            raise BadInput(
                "Focuses cannot be removed after character creation.")
        self._validate_attribute(player_id, attribute)
        attributes = self.player_characters[player_id].attributes
        if focus not in attributes[attribute]['focuses']:
            return "You did not have focus {} in attribute {}".format(
                focus, attribute,
            )
        attributes[attribute]['focuses'].remove(focus)
        return "Removed {} from {} focuses.".format(focus, attribute)

    def set_attribute(self, player_id, attribute, value):
        """Set an attribute to a specified value."""
        if not self.character_creation:
            raise BadInput(
                "Attributes can not be set after character creation.")
        self._validate_attribute(player_id, attribute)
        value = self._check_int(value)
        self.player_characters[player_id].attributes[attribute][
            'value'] = value
        return "{} set to {}".format(attribute, value)

    def set_skill(self, player_id, skill, value):
        """Set a skill to a specified value."""
        if not self.character_creation:
            raise BadInput("Skills can not be set after character creation.")
        value = self._check_int(value)
        char_skills = self.player_characters[player_id].skills
        if value == 0:
            if skill not in char_skills:
                raise BadInput(
                    "Can't remove {}- you don't have that skill.".format(
                        skill,
                    )
                )
            char_skills.pop(skill)
            return "Removed {} skill".format(skill)
        char_skills[skill] = value
        return "Set {} to {}".format(skill, value)

    def set_background(self, player_id, background, value):
        """Set a background to a specified value."""
        if not self.character_creation:
            raise BadInput(
                "Backgrounds can not be set after character creation.")
        value = self._check_int(value)
        char_bgs = self.player_characters[player_id].backgrounds
        if value == 0:
            if background not in char_bgs:
                raise BadInput(
                    "Can't remove {}- you don't have that background.".format(
                        background,
                    )
                )
            char_bgs.pop(background)
            return "Removed {} background".format(background)
        char_bgs[background] = value
        if background.lower() == 'generation':
            max_blood, blood_rate = {
                1: (10, 1),
                2: (12, 2),
                3: (15, 3),
                4: (20, 4),
                5: (30, 5),
            }[value]
            self.player_characters[player_id].blood['max'] = max_blood
            self.player_characters[player_id].blood['current'] = max_blood
            self.player_characters[player_id].blood['rate'] = blood_rate
        return "Set {} to {}".format(background, value)

    def set_discipline(self, player_id, discipline, value):
        """Set a discipline to a specified value."""
        if not self.character_creation:
            return "Backgrounds can not be set after character creation."
        value = self._check_int(value)
        char_disciplines = self.player_characters[player_id].disciplines
        if value == 0:
            if discipline not in char_disciplines:
                raise BadInput (
                    "Can't remove {}- you don't have that discipline.".format(
                        discipline,
                    )
                )
            char_disciplines.pop(discipline)
            return "Removed {} discipline".format(discipline)
        char_disciplines[discipline] = value
        return "Set {} to {}".format(discipline, value)

    def _validate_attribute(self, player_id, attribute):
        """Complain if an attribute isn't valid."""
        attributes = self.player_characters[player_id].attributes
        if attribute not in attributes:
            raise BadInput((
                "{} is not a valid attribute. Valid attributes are: {}"
            ).format(attribute, ','.join(attributes)))

    def _check_int(self, value):  # pylint: disable=R0201
        """Cast to integer, or complain."""
        try:
            return int(value)
        except ValueError:
            raise BadInput("{} is not an integer.".format(value))  # pylint: disable=W0707

    def _check_generation_is_set(self, player_id):
        """Check that the character's generation has been set."""
        if not self._get_generation(player_id):
            raise BadInput(
                "This command cannot be called until your Generation "
                "background has been set."
            )

    def _check_xp_available(self, player_id, cost):
        """Check the character has enough experience for something."""
        experience = self.player_characters[player_id].experience
        if cost > experience['current']:
            raise BadInput(
                "You need at least {} XP, but you only have {}".format(
                    cost, experience['current'],
                )
            )

    def _get_generation(self, player_id):
        """Get the generation of the character."""
        bgs = self.player_characters[player_id].backgrounds
        return bgs.get('generation') or bgs.get('Generation')

    def add_note(self, player_id, content):
        """Add a note to a character."""
        self.player_characters[player_id].notes.append(content)
        return "Note added."""

    def list_notes(self, player_id):
        """List notes on a character."""
        notes = self.player_characters[player_id].notes
        if notes:
            return "Your notes:\n" + "\n".join([
                '  {}: {}'.format(pos, note)
                for pos, note in enumerate(notes, start=1)
            ])
        return "You have no notes."

    def remove_note(self, player_id, pos):
        """Remove a note from a character (1-indexed for non-techies)."""
        pos = self._check_int(pos)
        notes = self.player_characters[player_id].notes
        if (pos - 1) < 0 or pos > len(notes):
            raise BadInput(
                "Note {} does not exist, you have {} notes.".format(
                    pos, len(notes)
                )
            )
        content = notes.pop(pos - 1)
        return "Removed note {}: {}".format(pos, content)

    def set_clan(self, player_id, clan):
        """Set a character's clan."""
        character = self.player_characters[player_id]
        if character.clan:
            raise BadInput("Your clan has already been set.")
        character.clan = clan
        return "Clan set to {}".format(clan)

    def increase_attribute(self, player_id, attribute):
        """Spend XP to increase an attribute on a character."""
        self._validate_attribute(player_id, attribute)
        self._check_generation_is_set(player_id)
        character = self.player_characters[player_id]

        cost = character.get_xp_costs()['Attribute']
        self._check_xp_available(player_id, cost)

        attributes = self.player_characters[player_id].attributes
        gen = self._get_generation(player_id)
        bonuses_spent = 0
        for current_attr in attributes.values():
            if current_attr['value'] > 10:
                bonuses_spent += (current_attr['value'] - 10)

        if (
            (bonuses_spent + 1) > gen
            and attributes[attribute]['value'] >= 10
        ):
            raise BadInput(
                "You don't have enough bonus points to raise {} any "
                "further.".format(attribute)
            )

        attributes[attribute]['value'] += 1
        message = "Raised {} to {}".format(
            attribute, attributes[attribute]['value']
        )
        character.spend_xp(cost, message)
        return message

    def _get_correct_case_entry(self, entry, current_list):  # pylint: disable=R0201
        """Normalise skill/discipline/background increases using an existing
        skill/discipline/background entry if it exists with a different case.
        """
        for current_value in current_list:
            if entry.lower() == current_value.lower():
                return current_value
        return entry

    def increase_skill(self, player_id, skill, exceed_maximum=False):
        """Increase a skill using xp."""
        self._check_generation_is_set(player_id)
        character = self.player_characters[player_id]
        skill = self._get_correct_case_entry(skill, character.skills)
        current_level = character.skills.get(skill, 0)

        cost_multiplier = int(
            character.get_xp_costs()['Skill'].split('x ')[1]
        )
        cost = (current_level + 1) * cost_multiplier
        self._check_xp_available(player_id, cost)

        if current_level == 5 and not exceed_maximum:
            raise BadInput(
                "You already have 5 points in this skill. "
                "This is the maximum unless you have a merit allowing more."
            )
        character.skills[skill] = current_level + 1
        message = "Raised {} to {}".format(
            skill, character.skills[skill],
        )
        character.spend_xp(cost, message)
        return message + " for {} XP".format(cost)

    def increase_background(self, player_id, background):
        """Increase a background using xp."""
        self._check_generation_is_set(player_id)
        character = self.player_characters[player_id]
        background = self._get_correct_case_entry(
            background, character.backgrounds)

        if background.lower() == 'generation':
            raise BadInput(
                "You can't buy generation improvements with XP, only by "
                "mercilessly draining the soul of someone stronger than "
                "you. You monster."
            )

        current_level = character.backgrounds.get(background, 0)

        cost_multiplier = int(
            character.get_xp_costs()['Background'].split('x ')[1]
        )
        cost = (current_level + 1) * cost_multiplier
        self._check_xp_available(player_id, cost)

        if current_level == 5:
            raise BadInput(
                "You already have 5 points in this background."
            )
        character.backgrounds[background] = current_level + 1
        message = "Raised {} to {}".format(
            background, character.backgrounds[background],
        )
        character.spend_xp(cost, message)
        return message + " for {} XP".format(cost)

    def add_merit(self, player_id, merit_name, cost):
        """Add a merit to a character."""
        character = self.player_characters[player_id]
        cost = self._check_int(cost)

        if merit_name.lower() in [item.lower() for item in character.merits]:
            raise BadInput('You already have the merit {}'.format(merit_name))

        current_merits_total = sum(character.merits.values())

        if current_merits_total + cost > 7:
            raise BadInput(
                'You may have at most 7 points of merits. You have {current} '
                'and are trying to add {new}, which would exceed 7.'.format(
                    current=current_merits_total,
                    new=cost,
                )
            )

        character.merits[merit_name] = cost
        return "Added merit {} with cost {}".format(merit_name, cost)

    def add_flaw(self, player_id, flaw_name, value):
        """Add a flaw to the character.
        During character creation there are a maximum of seven points of
        flaws and derangements and they award bonus XP.
        Later on, they do not award bonus XP, and have no limit."""
        character = self.player_characters[player_id]
        value = self._check_int(value)

        if flaw_name.lower() in [item.lower() for item in character.flaws]:
            raise BadInput('You already have the flaw {}'.format(flaw_name))

        if self.character_creation:
            self._check_flaws_and_derangements_limit(player_id, value)
            character.flaws[flaw_name] = value
            character.award_xp(value, "Took flaw: {}".format(flaw_name))
            return "Added flaw {} with value {} and gained XP.".format(
                flaw_name, value,
            )
        character.flaws[flaw_name] = value
        return "Inflicted flaw {} with value {}.".format(flaw_name, value)

    def add_derangement(self, player_id, derangement):
        """Add a derangement to the character.
        During character creation there are a maximum of seven points of
        flaws and derangements and they award bonus XP.
        Later on, they do not award bonus XP, and have no limit."""
        character = self.player_characters[player_id]

        if derangement.lower() in [item.lower()
                                   for item in character.derangements]:
            raise BadInput('You already have the derangement {}'.format(
                derangement))

        if self.character_creation:
            is_malkavian = character.clan.lower() == 'malkavian'
            value = 2
            if is_malkavian and len(character.derangements) == 0:
                value = 0
            self._check_flaws_and_derangements_limit(player_id, value)
            character.derangements.append(derangement)
            if value:
                character.award_xp(value, "Took derangement: {}".format(
                                   derangement))
                return "Added derangement {} for 2XP".format(derangement)
            return "Added derangement {} for Malkav's madness".format(
                derangement)
        character.derangements.append(derangement)
        return "Inflicted derangement {}".format(derangement)

    def _check_flaws_and_derangements_limit(self, player_id, value):
        """Check flaws/derangements limit will not be exceeded."""
        character = self.player_characters[player_id]
        if not character.clan:
            raise BadInput(
                "You must set your clan before adding derangements or flaws.")
        is_malkavian = character.clan.lower() == 'malkavian'
        current_flaws_total = sum(character.flaws.values())
        derangement_count = len(character.derangements)
        if is_malkavian:
            derangement_count = max(0, derangement_count - 1)
        current_flaws_total += (2 * derangement_count)
        if current_flaws_total + value > 7:
            raise BadInput(
                'You may have at most 7 points of flaws and '
                'derangements. You have {current} and are trying to add '
                '{new}, which would exceed 7.'.format(
                    current=current_flaws_total,
                    new=value,
                )
            )

    def remove_merit(self, player_id, merit):
        """Remove a merit."""
        character = self.player_characters[player_id]
        merit = self._get_correct_case_entry(merit, character.merits)

        try:
            value = character.merits.pop(merit)
            if self.character_creation:
                character.experience['current'] += value
                return "Removed {} and refunded {} XP".format(merit, value)
            return "Removed {}".format(merit)
        except KeyError:
            raise BadInput(  # pylint: disable=W0707
                'You did not have the merit {}'.format(merit)
            )

    def remove_flaw(self, player_id, flaw):
        """Remove or buy-off a flaw."""
        character = self.player_characters[player_id]
        flaw = self._get_correct_case_entry(flaw, character.flaws)

        if flaw not in character.flaws:
            raise BadInput("You did not have the flaw {}".format(flaw))

        message = "Removed flaw {}".format(flaw)
        value = character.flaws[flaw]
        if self.character_creation:
            character.flaws.pop(flaw)
            character.experience['current'] -= value
            character.experience['total'] -= value
            return message + ' removing {} XP'.format(value)
        self._check_xp_available(player_id, value)
        character.flaws.pop(flaw)
        character.spend_xp(value, message)
        return message + " for {} XP".format(value)

    def remove_derangement(self, player_id, derangement):
        """Remove or buy-off a derangement."""
        character = self.player_characters[player_id]
        derangement = self._get_correct_case_entry(
            derangement, character.derangements)

        if derangement not in character.derangements:
            raise BadInput("You did not have the derangement {}".format(
                derangement))

        if (
            character.clan.lower() == 'malkavian'
            and len(character.derangements) == 1
        ):
            raise BadInput("You cannot be any less deranged as a Malkavian.")

        message = "Removed derangement {}".format(derangement)
        value = 2
        if self.character_creation:
            character.derangements.remove(derangement)
            character.experience['current'] -= value
            character.experience['total'] -= value
            return message + ' removing {} XP'.format(value)
        self._check_xp_available(player_id, value)
        character.derangements.remove(derangement)
        character.spend_xp(value, message)
        return message + ' for {} XP'.format(value)

    def spend_willpower(self, player_id, amount):
        """Spend some willpower."""
        return self._spend_resource('willpower', player_id, amount)

    def spend_blood(self, player_id, amount):
        """Spend some blood."""
        return self._spend_resource('blood', player_id, amount)

    def _spend_resource(self, resource_type, player_id, amount):
        """Spend some temporary resources for a character."""
        character = self.player_characters[player_id]
        resource = {
            'blood': character.blood,
            'willpower': character.willpower,
        }[resource_type]
        amount = self._check_int(amount)
        if resource['current'] < amount:
            raise BadInput(
                'You cannot spend {} {}, you only have {}/{}'.format(
                    amount, resource_type, resource['current'],
                    resource['max'],
                )
            )
        resource['current'] -= amount
        return "You spent {} {} and have {}/{} remaining.".format(
            amount, resource_type, resource['current'], resource['max'],
        )

    def gain_willpower(self, player_id, amount):
        """Gain some willpower."""
        return self._gain_resource('willpower', player_id, amount)

    def gain_blood(self, player_id, amount):
        """Gain some blood."""
        return self._gain_resource('blood', player_id, amount)

    def gain_morality(self, player_id):
        """Gain a point of morality."""
        character = self.player_characters[player_id]
        if character.morality['current'] == character.morality['max']:
            raise BadInput('Your morality is at maximum already!')
        cost = 10
        message = 'Gain morality'
        character.spend_xp(cost, message)
        message = self._gain_resource('morality', player_id, 1)
        return message + " You spent 10 XP"

    def remove_morality(self, player_id):
        """Remove a point of morality."""
        character = self.player_characters[player_id]
        character.morality['current'] -= 1
        remaining = character.morality['current']
        message = "You lost 1 morality and now have {}.".format(remaining)
        if remaining == 0:
            message += " You have entered wassail, the final frenzy!"
        elif remaining < 3:
            message += (
                " You appear more pale and your bearing becomes feral."
                " Your flesh is cold and you no longer breathe or blink."
            )
        return message

    def _gain_resource(self, resource_type, player_id, amount):
        """Gain some temporary resources for a character."""
        character = self.player_characters[player_id]
        resource = {
            'blood': character.blood,
            'willpower': character.willpower,
            'morality': character.morality,
        }[resource_type]
        amount = self._check_int(amount)
        total = amount + resource['current']
        remaining = max(total - resource['max'], 0)
        gained = amount - remaining
        resource['current'] += gained
        message = "You gain {} {} and now have {}/{}.".format(
            gained, resource_type, resource['current'], resource['max'],
        )
        if remaining:
            message += (
                ' You could not gain {} due to reaching your maximum.'.format(
                    remaining,
                )
            )
        return message

    def gain_beast_traits(self, player_id, amount):
        """Gain beast traits."""
        character = self.player_characters[player_id]
        amount = self._check_int(amount)

        character.morality['beast traits'] += amount
        return (
            "You have gained {} beast traits. You now have {}.".format(
                amount, character.morality['beast traits'],
            )
        )

    def remove_beast_traits(self, player_id, amount):
        """Lose beast traits."""
        character = self.player_characters[player_id]
        amount = self._check_int(amount)

        character.morality['beast traits'] = max(
            character.morality['beast traits'] - amount,
            0
        )
        return (
            "You have lost {} beast traits. You now have {}.".format(
                amount, character.morality['beast traits'],
            )
        )

    def inflict_damage(self, player_id, damage_type, amount):
        """Inflict damage on a character."""
        character = self.player_characters[player_id]
        amount = self._check_int(amount)
        if damage_type not in ['aggravated', 'normal']:
            raise BadInput(
                'Damage type must be normal or aggravated.'
            )
        for _ in range(amount):
            character.damage_taken.append(damage_type)
        health_state = character.get_health_level()
        return (
            "You have taken {} {} damage, and are {}".format(
                amount, damage_type, health_state,
            )
        )

    def heal_damage(self, player_id, damage_type):
        """Heal damage on a character."""
        character = self.player_characters[player_id]
        if damage_type not in character.damage_taken:
            raise BadInput("You had no {} damage.".format(damage_type))
        character.damage_taken.remove(damage_type)
        normal = character.damage_taken.count('normal')
        aggravated = character.damage_taken.count('aggravated')
        health_state = character.get_health_level()
        return (
            "You healed a point of {} damage. "
            "You have {} normal and {} aggravated damage remaining. "
            "You are now {}.".format(
                damage_type, normal, aggravated, health_state,
            )
        )

    def finish_character_creation(self):
        """End character creation, begin the game proper!"""
        self.character_creation = False
        return "Character creation complete."

# TODO: No pdf output, give nice output
# TODO: Modify characters:
#   increase in-clan discipline (spending xp)
#   increase out-of-clan discipline (spending xp)
#   set name
#   undo
