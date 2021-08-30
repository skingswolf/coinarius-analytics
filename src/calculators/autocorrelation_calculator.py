import pandas as pd

from .correlation_calculator import CorrelationCalculator


class AutocorrelationCalculator(CorrelationCalculator):
    """
    Represents an class that calculates correlation of return of symbols
    with its own lagged returns
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
        get_other_symbol : str
            The other crypto symbol whose returns should be used
            in the correlation calculations.
        """
        super().__init__("autocorrelation", lambda symbol: symbol, return_calculator)

    def _calculate_correlation(self, returns, other_returns):
        """
        Calculate the correlation between the two given return series.

        Parameters
        ----------
        returns : double[]
            The returns series
        other_returns : double[]
            The other returns series

        Returns
        -------
            The correlation between the two given return series.
        """

        crypto_returns_df = pd.DataFrame(
            {"returns": returns, "other_returns": other_returns}
        )

        crypto_returns_df["returns"] = crypto_returns_df["returns"].shift(1)
        crypto_returns_df = crypto_returns_df.dropna()

        correlation_df = crypto_returns_df.corr()

        return correlation_df["returns"]["other_returns"]
