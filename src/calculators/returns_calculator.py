import numpy as np
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class ReturnsCalculator(AnalyticsCalculator):
    """
    Represents a class that calculates returns given price data.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        super().__init__("return")

    def _calculate_analytics(self, prices):
        """
        Calculate the analytics using the given prices.

        Parameters
        ----------
        prices : double[]
            An array of prices.

        Returns
        -------
            An array of the calculated analytics.
        """
        return np.diff(np.log(prices))

    def _calculate_latest_analytics(self, latest_price, prices, analytics):
        """
        Calculate the analytics using the given prices but only for the latest tick.

        Parameters
        ----------
        latest_price : double
            The latest tick price.
        prices : double[]
            An array of prices.
        analytics : double[
            An array of analytics values.

        Returns
        -------
            An array of the calculated analytics.
        """

        if len(prices) < 2:
            raise Exception(
                "There are insufficient price data points to calculate a singular return value."
            )

        in_scope_prices = [prices[-1], latest_price]
        new_log_return = np.diff(np.log(in_scope_prices))[-1]

        z_score = stats.zscore([*analytics, new_log_return])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": new_log_return,
            "last_z_score": z_score,
        }
