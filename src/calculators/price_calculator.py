from datetime import datetime
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class PriceCalculator(AnalyticsCalculator):
    """
    Represents a class that parses out prices from API response objects.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        super().__init__("price")

    def calculate(self, asset_data):
        """
        Calculates the price data for the given API price data.

        Parameters
        ----------
        price_data : dict
            API price data dictionary where relevant information
            is indexed by the keyword "data".

        Returns
        -------
            Price data dictionary indexed by symbol names.
        """
        price_data = {
            datum["symbol"]: self.__build_entry(datum) for datum in asset_data["data"]
        }

        return price_data

    def __build_entry(self, entry):
        """
        Constructs an analytics data dictionary entry given a
        price data dictionary entry.

        Returns
        -------
            An analytics data entry (i.e. a dictionary).
        """

        reformat_time = lambda t: datetime.fromtimestamp(t).strftime(
            "%Y-%m-%d, %H:%M:%S"
        )
        parse_time_series = lambda ts: [
            (
                reformat_time(ts_entry["time"]),
                ts_entry["close"],
            )
            for ts_entry in ts
        ]

        parsed_time_series = parse_time_series(entry["timeSeries"])

        last_price = entry["price"]
        prices = [entry[1] for entry in parsed_time_series]
        prices.append(last_price)
        z_score = stats.zscore(prices)[-1]

        return {
            "time_series": parsed_time_series,
            "last_price": last_price,
            "last_z_score": z_score,
        }
