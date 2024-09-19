class CanInterfaceNotImplementedError(Exception):
    """
    Error raised when CAN interface could not be initialized
    because of incorrect interface data provided.
    """
    pass


class CanInitializationError(Exception):
    """
    Error raised when CAN interface could not be initialized
    because of other errors.
    """
    pass
