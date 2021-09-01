"""Session management for vampire sessions."""
from .sheet import Character

class Session:
    """Vampire session manager."""
    player_characters = {}

    def load(self, session_save_path):
        """Load the game from its save path."""
        # TODO

    def add_player(self, player_id, player_name):
        """Add a player to the game."""
        if player_id in self.player_characters:
            return "{} has already joined.".format(player_name)
        self.player_characters[player_id] = Character()
        self.player_characters[player_id].player = player_name
        return "Added {}.".format(player_name)

    def award_xp(self, amount, reason):
        for character in self.player_characters.values():
            character.award_xp(amount, reason)

    def get_player_json(self, player_id):
        """Get the json of a particular player's character sheet."""
        return self.player_characters[player_id].to_json()

# TODO: No pdf output, give nice output
# TODO: Modify characters
