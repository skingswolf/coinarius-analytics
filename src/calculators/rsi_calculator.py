import numpy as np
import pandas as pd
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class RsiCalculator(AnalyticsCalculator):
    """
    Represents a class that calculates a relative strength momentum (rsi) values.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        super().__init__("rsi", "price")

        self.__num_periods = 14

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
        rsi_values = self.__calculate_rsi(prices)

        return rsi_values

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

        if len(fundamentals) < self.__num_periods + 1:
            raise Exception(
                "There are insufficient price data points to calculate a singular moving average value."
            )

        in_scope_prices = (
            fundamentals[-(self.__num_periods + 1) :]
            if latest_fundamental is None
            else [*fundamentals[-(self.__num_periods + 1) : -1], latest_fundamental]
        )

        new_rsi = self.__calculate_rsi(in_scope_prices)[-1]
        z_score = stats.zscore([*analytics[:-1], new_rsi])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": new_rsi,
            "last_z_score": z_score,
        }

    def __calculate_rsi(self, prices):
        """
        Calculates the rsi values for the given prices.

        Parameters
        ----------
        prices : double[]
            The prices.

        Returns
        -------
            The rsi values for the given prices.
        """

        # TODO: implement this algorithm without dataframes.
        prices_df = pd.DataFrame(prices, columns=["price"])

        price_change = prices_df["price"].diff()
        increases = price_change.clip(lower=0)
        decreases = -1 * price_change.clip(upper=0)

        moving_average_increases = increases.ewm(
            com=self.__num_periods - 1, adjust=True, min_periods=self.__num_periods
        ).mean()
        moving_average_decreases = decreases.ewm(
            com=self.__num_periods - 1, adjust=True, min_periods=self.__num_periods
        ).mean()

        rsi = moving_average_increases / moving_average_decreases
        rsi = 100 - (100 / (1 + rsi))
        rsi = rsi.dropna()

        rsi_values = list(filter(None, rsi.values.tolist()))

        return rsi_values
