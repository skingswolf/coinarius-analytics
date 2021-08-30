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
        id : str
            The ID of this correlation calculator.
        return_calculator : ReturnCalculator
            Returns calculator.
        other_symbol : str
            The other crypto symbol whose returns should be used
            in the correlation calculations.
        """
        super().__init__("eth_correlation", "ETH", return_calculator)
