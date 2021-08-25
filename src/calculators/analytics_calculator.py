import scipy.stats as stats

from utils.logger import Logger


class AnalyticsCalculator:
    """
    Represents a class that calculates analytics given price data.

    ...

    Instance Attributes
    ----------
    _logger : Logger
        The logger of this class.
    id : string
        An ID for the calculator which is simply the name of the analytics being calculated.
    price_data : dict
        Price data dictionary indexed by symbol names.
    analytics_data : dict
        Analytics data dictionary indexed by symbol names.
    """

    def __init__(self, analytics_id):
        """
        Initialises a new instance of this class.
        """
        self._logger = Logger.get_instance()
        self.id = analytics_id
        self.price_data = None
        self.analytics_data = None

    def calculate(self, price_data):
        """
        Calculates the analytics data for the given price data.

        Parameters
        ----------
        price_data : dict
            Price data dictionary.

        Returns
        -------
            Analytics data dictionary indexed by symbol names.
        """

        self._logger.log(f"Calculating {self.id} data for all symbols.")

        self.price_data = price_data
        self.analytics_data = {
            symbol: self.__build_entry(symbol, price_data[symbol])
            for symbol in price_data
        }

        return self.analytics_data

    def calculate_latest(self, latest_prices):
        """
        Calculates the analytics only for the most recent tick.

        Parameters
        ----------
        latest_prices : dict
            The latest tick prices dictionary indexed by symbol.

        Returns
        -------
            Analytics data dictionary indexed by symbol names but where the
        """

        if self.price_data is None or self.analytics_data is None:
            raise Exception(
                "Both caches for price and analytics data are null - run `calculate` to initialise them."
            )

        return {
            symbol: self._calculate_latest_analytics(
                latest_prices[symbol],
                [entry[1] for entry in self.price_data[symbol]["time_series"]],
                [entry[1] for entry in self.analytics_data[symbol]["time_series"]],
            )
            for symbol in self.analytics_data.keys()
        }

    def __build_entry(self, symbol, entry):
        """
        Constructs an analytics data dictionary entry given a
        price data dictionary entry.

        Parameters
        ----------
        symbol: str
            The asset symbol.
        entry: dict
            Dictionary with key value pairs corresponding to the price time series,
            last tick price and the z score for the last tick price.
        Returns
        -------
            An analytics data entry (i.e. a dictionary).
        """

        self._logger.log(
            f"Building entry for {self.id} data for the asset symbol {symbol}."
        )

        prices = [entry[1] for entry in entry["time_series"]]
        time_datapoints = [entry[0] for entry in entry["time_series"]]
        analytics = self._calculate_analytics([*prices, entry["last_price"]])

        last_analytics_value = analytics[-1]
        z_score = stats.zscore(analytics)[-1]

        analytics_time_series = list(zip(time_datapoints, analytics[:-1]))

        return {
            "time_series": analytics_time_series,
            f"last_{self.id}": last_analytics_value,
            "last_z_score": z_score,
        }

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

        raise NotImplementedError(
            "analytics_generator is a base class and this method should be implemented in its child classes."
        )

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
        raise NotImplementedError(
            "analytics_generator is a base class and this method should be implemented in its child classes."
        )
