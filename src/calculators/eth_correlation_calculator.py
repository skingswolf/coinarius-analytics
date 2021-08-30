from .correlation_calculator import CorrelationCalculator


class EthCorrelationCalculator(CorrelationCalculator):
    """
    Represents an class that calculates correlation of return of symbols
    with Ethereum's returns.
    """

    def __init__(self, return_calculator):
        """
        Initialises a new instance of this class.

        Parameters
        ----------
        return_calculator : ReturnCalculator
            The return calculator.
        """
        super().__init__("eth_correlation", lambda symbol: "ETH", return_calculator)
