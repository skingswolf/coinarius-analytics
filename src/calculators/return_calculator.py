import numpy as np
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class ReturnCalculator(AnalyticsCalculator):
    """
    Represents a class that calculates returns given price data.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        super().__init__("return", "price")

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
        return np.diff(np.log(list(filter(None, fundamentals))))

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
                "There are insufficient price data points to calculate a singular return value."
            )

        in_scope_prices = [fundamentals[-1], latest_fundamental]
        new_log_return = np.diff(np.log(in_scope_prices))[-1]

        z_score = stats.zscore([*analytics, new_log_return])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": new_log_return,
            "last_z_score": z_score,
        }
