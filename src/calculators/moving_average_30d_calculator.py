import numpy as np
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class MovingAverage30dCalculator(AnalyticsCalculator):
    """
    Represents a class that calculates a simple moving average with a window of 30 days.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        super().__init__("moving_average_30d", "price")

        self.__window = 30

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
        moving_averages = self.__calculate_moving_average(prices)

        return moving_averages

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

        if len(fundamentals) < self.__window:
            raise Exception(
                "There are insufficient price data points to calculate a singular moving average value."
            )

        in_scope_prices = (
            fundamentals[-self.__window :]
            if latest_fundamental is None
            else [*fundamentals[-self.__window : -1], latest_fundamental]
        )

        new_moving_average = self.__calculate_moving_average(in_scope_prices)[-1]
        z_score = stats.zscore([*analytics[:-1], new_moving_average])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": new_moving_average,
            "last_z_score": z_score,
        }

    def __calculate_moving_average(self, prices):
        """
        Calculates the 30 day moving averages for the given prices.

        Parameters
        ----------
        prices : double[]
            The prices.

        Returns
        -------
            The 30 day moving averages for the given prices.
        """

        cum_sum_prices = np.cumsum(np.insert(prices, 0, 0))

        return (
            cum_sum_prices[self.__window :] - cum_sum_prices[: -self.__window]
        ) / float(self.__window)
