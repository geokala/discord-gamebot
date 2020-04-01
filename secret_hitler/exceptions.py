"""Exceptions for secret hitler."""

class GameAlreadyRunning(Exception):
    """Raised by the manager when trying to create a game with the same ID as
    an existing game."""


class GameNotRunning(Exception):
    """Raised by the manager when asked to operate on a game ID that does not
    exist."""


class InvalidPolicyType(Exception):
    """Raised by the game when an invalid policy is selected."""


class GameEnded(Exception):
    """Raised by the game when trying to act on a finished game."""


class GameInProgress(Exception):
    """Raised by the game when attempting to prepare for a game that has
    already started."""


class GameNotStarted(Exception):
    """Raised by the game when attempting to get information which requires
    the game to have started before starting it."""


class NotEnoughPlayers(Exception):
    """Raised by the game when attempting to start with not enough players."""


class PlayerLimitReached(Exception):
    """Raised by the game when attempting to add a player to a full game."""


class NotPresidentTurn(Exception):
    """Raised by the game when attempting to discard a presidential policy
    card outside of the President's turn."""


class VetoNotAllowed(Exception):
    """Raised by the game when a veto is attempted before it is allowed."""
