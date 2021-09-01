class SymbolStore:
    """
    Represents a store containing all symbols in the coinarius analytics universe.
    """

    __instance = None

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        self.symbol_map = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "LTC": "Litecoin",
            "BCH": "Bitcoin Cash",
            "DOGE": "Dogecoin",
        }
        self.symbols = self.symbol_map.keys()

        if SymbolStore.__instance is not None:
            raise Exception("SymbolStore class is a Singleton!")
        else:
            SymbolStore.__instance = self

    @staticmethod
    def get_instance():
        """
        Returns the single instance of this SymbolStore class.
        """

        if SymbolStore.__instance is None:
            SymbolStore()

        return SymbolStore.__instance

    def __str__(self):
        """
        Returns a comma separated string list of symbols.

        Returns
        -------
            A comma separated string list of symbols.
        """

        return ",".join(self.symbols)
