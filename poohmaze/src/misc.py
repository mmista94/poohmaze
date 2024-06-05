import enum

class GameState(enum.Enum):
    """
    Enum for the Game's State Machine. Every state represents a
    known game state for the game engine.
    """

    # Unknown state, indicating possible error or misconfiguration.
    unknown = "unknown"
    starting = "starting"
    initializing_maze = "initializing_maze"
    display_initialized = "display_initialized"
    initialized = "initialized"
    gameplay = "gameplay"
    resizing = "resizing"
    quitting = "quitting"
    

class StateError(Exception):
    """
    Raised if the game is in an unexpected game state at a point
    where we expect it to be in a different state. For instance, to
    start the game loop we must be initialized.
    """