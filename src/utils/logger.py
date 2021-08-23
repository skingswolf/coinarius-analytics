class Logger:
    """
    Logger class which follows the Singleton pattern.
    ...

    Class Attributes
    ----------
    __instance : Logger
        The singular instance of this Logger class.
    debug_mode : bool
        A flag which when set to `True` includes detailed messages
        intended for diagnostic purposes in this Logger's output.
    Methods
    -------
    get_instance()
        Returns the single instance of this Logger class.
    log(message)
        Logs the message.
    debug(message)
        Logs a detailed message intended for diagnostic purposes.
    """

    __instance = None

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        if Logger.__instance is not None:
            raise Exception("Logger class is a Singleton!")
        else:
            Logger.__instance = self

    @staticmethod
    def get_instance():
        """
        Returns the single instance of this Logger class.
        """

        if Logger.__instance is None:
            Logger()

        return Logger.__instance

    @staticmethod
    def log(message):
        """
        Logs the message.
        Parameters
        ----------
        message : str
            The message to be logged.
        """

        print(message)
