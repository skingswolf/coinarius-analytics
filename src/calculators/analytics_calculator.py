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
    id : string
        An ID for the fundamental data, e.g. price or valume, which underpins the analytics being calculated.
    fundamental_data : dict
        Price data dictionary indexed by symbol names.
    analytics_data : dict
        Analytics data dictionary indexed by symbol names.
    """

    def __init__(self, analytics_id, fundamental_id, is_fundamental=False):
        """
        Initialises a new instance of this class.
        """
        self._logger = Logger.get_instance()
        self.id = analytics_id
        self.fundamental_id = fundamental_id
        self.is_fundamental = is_fundamental
        self.fundamental_data = None
        self.analytics_data = None
        self.latest_analytics_data = None

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

        self.fundamental_data = fundamental_data
        self.analytics_data = {
            symbol: self.__build_entry(symbol, fundamental_data[symbol])
            for symbol in fundamental_data
        }

        return self.analytics_data

    def calculate_latest(self, latest_fundamentals):
        """
        Calculates the analytics only for the most recent tick.

        Parameters
        ----------
        latest_fundamentals : dict
            The latest tick fundamentals (e.g. price or volume) dictionary indexed by symbol.

        Returns
        -------
            Analytics data dictionary indexed by symbol names but where the
        """

        if self.fundamental_data is None or self.analytics_data is None:
            raise Exception(
                f"Both caches for {self.fundamental_id} and analytics data are null - run `calculate` to initialise them."
            )

        self.latest_analytics_data = {
            symbol: self._calculate_latest_analytics(
                latest_fundamentals[symbol][self.fundamental_id],
                [entry[1] for entry in self.fundamental_data[symbol]["time_series"]],
                [entry[1] for entry in self.analytics_data[symbol]["time_series"]],
            )
            for symbol in self.analytics_data.keys()
        }

        return self.latest_analytics_data

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

        fundamentals = [entry[1] for entry in entry["time_series"]]
        time_datapoints = [entry[0] for entry in entry["time_series"]]
        analytics = self._calculate_analytics(
            [*fundamentals[:-1], entry[f"last_{self.fundamental_id}"]]
        )

        filtered_analytics = list(filter(None, analytics))
        last_analytics_value = filtered_analytics[-1]
        z_score = stats.zscore(filtered_analytics)[-1]

        analytics_time_series = list(
            zip(time_datapoints[-len(filtered_analytics) :], filtered_analytics)
        )

        return {
            "time_series": analytics_time_series,
            f"last_{self.id}": last_analytics_value,
            "last_z_score": z_score,
        }

    def _calculate_analytics(self, fundamentals):
        """
        Calculate the analytics using the given fundamentals.

        Parameters
        ----------
        fundamentals : double[]
            An array of fundamentals - a.g. fundamentals or volumes.

        Returns
        -------
            An array of the calculated analytics.
        """

        raise NotImplementedError(
            "analytics_generator is a base class and this method should be implemented in its child classes."
        )

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
        raise NotImplementedError(
            "analytics_generator is a base class and this method should be implemented in its child classes."
        )
