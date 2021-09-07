"""Session management for vampire sessions."""
from .sheet import Character


class BadInput(Exception):
    """Raised when bad input is supplied by the frontend."""


class Session:
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

    def finish_character_creation(self):
        """End character creation, begin the game proper!"""
        self.character_creation = False
        return "Character creation complete."

# TODO: No pdf output, give nice output
# TODO: Modify characters:
#   remove merit
#   add flaw
#   remove flaw (opt: using xp)
#   add derangement
#   spend willpower
#   restore willpower to all characters
#   add beast traits to character
#   add damage to character
#   remove normal damage from character (opt: spending blood)
#   remove agg damage from character (opt: spending blood)
#   spend blood
#   gain blood
#   increase in-clan discipline (spending xp)
#   increase out-of-clan discipline (spending xp)
#   set name
#   set clan
