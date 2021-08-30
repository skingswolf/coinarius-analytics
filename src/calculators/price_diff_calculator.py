import numpy as np
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class PriceDiffCalculator(AnalyticsCalculator):
    """
    Represents a class that calculates price differences given price data.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        super().__init__("price_diff", "price")

    def _calculate_analytics(self, fundamentals):
        """
        Calculate the analytics using the given fundamentals.

        Parameters
        ----------
        fundamentals : double[]
            An array of fundamentals.

        Returns
        -------
            An array of the calculated analytics.
        """
        prices = list(filter(None, fundamentals))

        price_diffs = np.diff(prices)

        return price_diffs

    def _calculate_latest_analytics(self, latest_fundamental, fundamentals, analytics):
        """
        Calculate the analytics using the given fundamentals but only for the latest tick.

        Parameters
        ----------
        latest_fundamental : double
            The latest tick price.
        fundamentals : double[]
            An array of fundamentals.
        analytics : double[
            An array of analytics values.

        Returns
        -------
            An array of the calculated analytics.
        """

        if len(fundamentals) < 2:
            raise Exception(
                "There are insufficient price data points to calculate a singular price difference value."
            )

        in_scope_prices = (
            fundamentals[-2:]
            if latest_fundamental is None
            else [fundamentals[-2], latest_fundamental]
        )

        new_price_diff = np.diff(in_scope_prices)[-1]
        z_score = stats.zscore([*analytics[:-1], new_price_diff])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": new_price_diff,
            "last_z_score": z_score,
        }
