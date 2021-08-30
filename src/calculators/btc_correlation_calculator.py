from .correlation_calculator import CorrelationCalculator


class BtcCorrelationCalculator(CorrelationCalculator):
    """
    Represents an class that calculates correlation of return of symbols
    with Bitcoin's returns.
    """

    def __init__(self, return_calculator):
        """
        Initialises a new instance of this class.

        Parameters
        ----------
        return_calculator : ReturnCalculator
            The returns calculator.
        """
        super().__init__("btc_correlation", lambda symbol: "BTC", return_calculator)
