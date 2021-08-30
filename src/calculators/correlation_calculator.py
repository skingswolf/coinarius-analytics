import pandas as pd

from .analytics_calculator import AnalyticsCalculator


class CorrelationCalculator(AnalyticsCalculator):
    """
    Represents an abstract class that calculates returns looking back at 30 days worth of prices.
    """

    def __init__(self, id, get_other_symbol, return_calculator):
        """
        Initialises a new instance of this class.

        Parameters
        ----------
        id : str
            The ID of this correlation calculator.
        return_calculator : ReturnCalculator
            Returns calculator.
        get_other_symbol : func
            Function that returns the other crypto symbol whose returns
            should be used in the correlation calculations.
        """
        super().__init__(id, "price")
        self.__get_other_symbol = get_other_symbol
        self.__return_calculator = return_calculator

    def calculate(self, fundamental_data):
        """
        Calculates the analytics data for the given price data.

        Parameters
        ----------
        fundamental_data : dict
            Price data dictionary.

        Returns
        -------
            Analytics data dictionary indexed by symbol names.
        """

        self._logger.log(f"Calculating {self.id} data for all symbols.")

        return_data = self.__return_calculator.analytics_data

        if return_data is None:
            raise Exception(
                "The return calculator hasn't executed it's `calculate` method - there are no available return values to calculate correlation values for."
            )

        self.fundamental_data = fundamental_data
        self.analytics_data = {
            symbol: self.__build_correlation_entry(
                symbol,
                return_data[symbol],
                return_data[self.__get_other_symbol(symbol)],
            )
            for symbol in fundamental_data
        }

        return self.analytics_data

    def calculate_latest(self, _):
        """
        Calculates the analytics only for the most recent tick.

        Parameters
        ----------
        _ : dict
            The latest tick fundamentals (e.g. price or volume) dictionary indexed by symbol.

        Returns
        -------
            Analytics data dictionary indexed by symbol names but where the
        """

        return_data = self.__return_calculator.analytics_data
        latest_return_data = self.__return_calculator.analytics_data

        if self.fundamental_data is None or self.analytics_data is None:
            raise Exception(
                f"Both caches for return_data and latest_return_data data are null - run `calculate` in the return_calculator to initialise them."
            )

        self.latest_analytics_data = {
            symbol: self._calculate_latest_correlation_analytics(
                latest_return_data[symbol]["last_return"],
                latest_return_data[self.__get_other_symbol(symbol)]["last_return"],
                [entry[1] for entry in return_data[symbol]["time_series"]],
                [
                    entry[1]
                    for entry in return_data[self.__get_other_symbol(symbol)][
                        "time_series"
                    ]
                ],
            )
            for symbol in self.analytics_data.keys()
        }

        return self.latest_analytics_data

    def __build_correlation_entry(self, symbol, symbol_entry, other_symbol_entry):
        """
        Constructs an analytics data dictionary entry given a
        price data dictionary entry.

        Parameters
        ----------
        symbol: str
            The asset symbol.
        symbol_entry: dict
            Dictionary with key value pairs corresponding to the return time series,
            last tick price and the z score for the last tick price.
        other_symbol_entry: dict
            Dictionary with key value pairs corresponding to the return time series,
            last tick price and the z score for the last tick price.
        Returns
        -------
            An analytics data entry (i.e. a dictionary).
        """

        self._logger.log(
            f"Building entry for {self.id} data for the asset symbol {symbol}."
        )

        returns = [entry[1] for entry in symbol_entry["time_series"]]
        other_returns = [entry[1] for entry in other_symbol_entry["time_series"]]
        time_datapoints = [entry[0] for entry in symbol_entry["time_series"]]

        correlation = self._calculate_correlation_analytics(returns, other_returns)

        return {
            "time_series": None,
            f"last_{self.id}": correlation,
            "last_z_score": None,
        }

    def _calculate_correlation_analytics(self, returns, other_returns):
        """
        Calculates the crypto returns correlation (singular) using the given returnss.

        Parameters
        ----------
        returns : double[]
            An array of returns corresponding the asset `symbol`.
        other_returns : double[]
            An array of returns corresponding the asset `get_other_symbol`.
        Returns
        -------
            The calculated correlation.
        """

        returns = list(filter(None, returns))
        other_returns = list(filter(None, other_returns))

        return self._calculate_correlation(returns, other_returns)

    def _calculate_latest_correlation_analytics(
        self, latest_return, latest_other_return, returns, other_returns
    ):
        """
        Calculate the analytics using the given fundamentals but only for the latest tick.

        Parameters
        ----------
        latest_return : double
            The latest return.
        latest_other_return : double
            The latest return for the other symbol.
        returns : double[]
            An array of fundamentals.
        other_returns : double[
            An array of analytics values.

        Returns
        -------
            An array of the calculated analytics.
        """

        returns = [*returns[:-1], latest_return]
        other_returns = [*other_returns[:-1], latest_other_return]

        returns = list(filter(None, returns))
        other_returns = list(filter(None, other_returns))

        correlation = self._calculate_correlation(returns, other_returns)

        return {
            "time_series": None,
            f"last_{self.id}": correlation,
            "last_z_score": None,
        }

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

        correlation_df = crypto_returns_df.corr()

        return correlation_df["returns"]["other_returns"]
