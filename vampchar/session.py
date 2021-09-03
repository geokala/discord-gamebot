"""Session management for vampire sessions."""
from .sheet import Character

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
            return "{} has already joined.".format(player_name)
        self.player_characters[player_id] = Character()
        self.player_characters[player_id].player = player_name
        return "Added {}.".format(player_name)

    def award_xp(self, amount, reason):
        """Award all players some XP for a given reason."""
        for character in self.player_characters.values():
            character.award_xp(amount, reason)

    def get_player_json(self, player_id):
        """Get the json of a particular player's character sheet."""
        return self.player_characters[player_id].to_json()

    def add_focus(self, player_id, attribute, focus):
        """Add a focus on a given attribute."""
        if not self.character_creation:
            return "Focuses cannot be added after character creation."
        attributes = self.player_characters[player_id].attributes
        attrib_check = self._validate_attribute(player_id, attribute)
        if attrib_check:
            return attrib_check
        if focus in attributes[attribute]['focuses']:
            return "You already have focus {} in attribute {}".format(
                focus, attribute,
            )
        attributes[attribute]['focuses'].append(focus)
        return "Added {} to {} focuses.".format(focus, attribute)

    def remove_focus(self, player_id, attribute, focus):
        """Remove a focus from a given attribute."""
        if not self.character_creation:
            return "Focuses cannot be removed after character creation."
        attributes = self.player_characters[player_id].attributes
        attrib_check = self._validate_attribute(player_id, attribute)
        if attrib_check:
            return attrib_check
        if focus not in attributes[attribute]['focuses']:
            return "You did not have focus {} in attribute {}".format(
                focus, attribute,
            )
        attributes[attribute]['focuses'].remove(focus)
        return "Removed {} from {} focuses.".format(focus, attribute)

    def set_attribute(self, player_id, attribute, value):
        """Set an attribute to a specified value."""
        if not self.character_creation:
            return "Attributes can not be set after character creation."
        attrib_check = self._validate_attribute(player_id, attribute)
        if attrib_check:
            return attrib_check
        self.player_characters[player_id].attributes[attribute][
            'value'] = value
        return "{} set to {}".format(attribute, value)

    def set_skill(self, player_id, skill, value):
        """Set a skill to a specified value."""
        if not self.character_creation:
            return "Skills can not be set after character creation."
        char_skills = self.player_characters[player_id].skills
        if value == 0:
            if skill not in char_skills:
                return "Can't remove {} as you don't have that skill.".format(
                    skill,
                )
            char_skills.pop(skill)
            return "Removed {} skill".format(skill)
        char_skills[skill] = value
        return "Set {} to {}".format(skill, value)

    def set_background(self, player_id, background, value):
        """Set a background to a specified value."""
        if not self.character_creation:
            return "Backgrounds can not be set after character creation."
        char_bgs = self.player_characters[player_id].backgrounds
        if value == 0:
            if background not in char_bgs:
                return (
                    "Can't remove {} as you don't have that background."
                ).format(background)
            char_bgs.pop(background)
            return "Removed {} background".format(background)
        char_bgs[background] = value
        return "Set {} to {}".format(background, value)

    def set_discipline(self, player_id, discipline, value):
        """Set a discipline to a specified value."""
        if not self.character_creation:
            return "Backgrounds can not be set after character creation."
        char_disciplines = self.player_characters[player_id].disciplines
        if value == 0:
            if discipline not in char_disciplines:
                return (
                    "Can't remove {} as you don't have that discipline."
                ).format(discipline)
            char_disciplines.pop(discipline)
            return "Removed {} discipline".format(discipline)
        char_disciplines[discipline] = value
        return "Set {} to {}".format(discipline, value)

    def _validate_attribute(self, player_id, attribute):
        """Complain if an attribute isn't valid."""
        attributes = self.player_characters[player_id].attributes
        if attribute not in attributes:
            return (
                "{} is not a valid attribute. Valid attributes are: {}"
            ).format(attribute, ','.join(attributes))
        return ""

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
        notes = self.player_characters[player_id].notes
        if (pos - 1) < 0 or pos > len(notes):
            return (
                "Note {} does not exist, you have {} notes."
            ).format(pos, len(notes))
        content = notes.pop(pos - 1)
        return "Removed note {}: {}".format(pos, content)

    def finish_character_creation(self):
        """End character creation, begin the game proper!"""
        self.character_creation = False
        return "Character creation complete."

# TODO: No pdf output, give nice output
# TODO: Modify characters:
#   add to attribute (using xp)
#   increase skill (using xp)
#   increase background (ousing xp)
#   add merit (opt: using xp)
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
