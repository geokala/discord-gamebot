"""Management for games of secret hitler."""
from secret_hitler.exceptions import (
    GameAlreadyRunning,
    GameNotRunning,
)
from secret_hitler.game import Game


class GameTracker:
    """Class for tracking running games of secret hitler and updating
    stats on completion."""

    stats = {
        'Liberal win (policies)': 0,
        'Liberal win (killed Hitler)': 0,
        'Fascist win (policies)': 0,
        'Fascist win (chancellor Hitler)': 0,
        'Cancelled games': 0,
        'Currently running games': 0,
        'Total completed games': 0,
    }
    current_games = {}

    def start_game(self, game_id, first_player_id):
        """Start a game of secret hitler.
        :param game_id: A string ID for the game.

        :return: The new game.

        :raises GameAlreadyRunning: Raised if game ID is already in use."""
        if game_id in self.current_games:
            raise GameAlreadyRunning(
                'A game with ID {} already exists.'.format(game_id)
            )

        self.current_games[game_id] = Game()
        self.current_games[game_id].add_player(first_player_id)
        self.stats['Currently running games'] += 1
        return self.current_games[game_id]

    def cancel_game(self, game_id):
        """Cancel a running game.
        :param game_id: The string ID of the game to cancel.

        :raises GameNotRunning: Raised if game ID is not a running game."""
        if game_id in self.current_games:
            self.current_games.pop(game_id)
            self.stats['Cancelled games'] += 1
            self.stats['Currently running games'] -= 1
        else:
            raise GameNotRunning(
                '{} was not a running game.'.format(game_id),
            )

    def update_game_on_completion(self, game_id):
        """Check if a game is finished, and add it to the stats if so.
        :param game_id: The string ID of the game to check for completion.

        :return: None if the game is not finished, or one of the win states.

        :raises GameNotRunning: Raised if game ID is not a running game."""
        if game_id in self.current_games:
            state = self.current_games[game_id]
            if state is not None:
                self.stats[state] += 1
                self.stats['Currently running games'] -= 1
                self.current_games.remove(game_id)
            return state

        raise GameNotRunning(
            '{} was not a running game.'.format(game_id),
        )
