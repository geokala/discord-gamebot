"""Exceptions for secret hitler."""

class GameAlreadyRunning(Exception):
    """Exception raised by the manager when trying to create a game with the
    same ID as an existing game."""


class GameNotRunning(Exception):
    """Exception raised by the manager when asked to operate on a game ID
    that does not exist."""
