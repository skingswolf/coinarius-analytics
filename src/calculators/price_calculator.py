from datetime import datetime
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class PriceCalculator(AnalyticsCalculator):
    """
    Represents a class that parses out fundamentals from API response objects.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        super().__init__("price", "price", is_fundamental=True)

    def calculate(self, asset_data):
        """
        Calculates the price data for the given API price data.

        Parameters
        ----------
        fundamental_data : dict
            API price data dictionary where relevant information
            is indexed by the keyword "data".

        Returns
        -------
            Price data dictionary indexed by symbol names.
        """
        price_data = {
            datum["symbol"]: self.__build_entry(datum["symbol"], datum)
            for datum in asset_data["data"]
        }

        self.fundamental_data = price_data
        self.analytics_data = price_data

        return price_data

    def __build_entry(self, symbol, entry):
        """
        Constructs an analytics data dictionary entry given a
        raw asset data data dictionary entry.

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

        reformat_time = lambda t: datetime.fromtimestamp(t).strftime(
            "%Y-%m-%d, %H:%M:%S"
        )
        parse_time_series = lambda ts: [
            [
                reformat_time(ts_entry["time"]),
                ts_entry["close"],
            ]
            for ts_entry in ts
        ]

        last_price = entry["price"]
        parsed_time_series = parse_time_series(entry["timeSeries"])
        parsed_time_series[-1][1] = last_price
        prices = [entry[1] for entry in parsed_time_series if entry[1] is not None]
        z_score = stats.zscore(prices)[-1]

        return {
            "time_series": parsed_time_series,
            "last_price": last_price,
            "last_z_score": z_score,
        }

    def _calculate_latest_analytics(self, latest_fundamental, fundamentals, analytics):
        """
        Calculate the analytics using the given fundamentals but only for the latest tick.

        Parameters
        ----------
        latest_fundamental : double
            The latest tick fundamentals.
        fundamentals : double[]
            An array of fundamentals.
        analytics : double[]
            An array of analytics values.

        Returns
        -------
            An array of the calculated analytics.
        """

        fundamentals_in_scope = (
            fundamentals
            if latest_fundamental is None
            else [*fundamentals[:-1], latest_fundamental]
        )

        z_score = stats.zscore(fundamentals_in_scope)[-1]

        return {
            "time_series": None,
            f"last_{self.id}": latest_fundamental,
            "last_z_score": z_score,
        }
