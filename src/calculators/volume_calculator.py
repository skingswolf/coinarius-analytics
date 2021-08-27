from datetime import datetime
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class VolumeCalculator(AnalyticsCalculator):
    """
    Represents a class that parses out volume values from API response objects.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        super().__init__("volume", "volume", is_fundamental=True)

    def calculate(self, asset_data):
        """
        Calculates the volume data for the given API volume data.

        Parameters
        ----------
        asset_data : dict
            API time_series data dictionary where relevant information
            is indexed by the keyword "data".

        Returns
        -------
            Price data dictionary indexed by symbol names.
        """
        volume_data = {
            datum["symbol"]: self.__build_entry(datum["symbol"], datum)
            for datum in asset_data["data"]
        }

        self.analytics_data = volume_data
        self.fundamental_data = volume_data

        return volume_data

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
            (
                reformat_time(ts_entry["time"]),
                ts_entry["volume"],
            )
            for ts_entry in ts
        ]

        parsed_time_series = parse_time_series(entry["timeSeries"])

        volume_price = entry["volume"]
        volumes = [entry[1] for entry in parsed_time_series if entry[1] is not None]
        z_score = stats.zscore([*volumes, volume_price])[-1]

        return {
            "time_series": parsed_time_series,
            "last_volume": volume_price,
            "last_z_score": z_score,
        }

    def _calculate_latest_analytics(self, latest_volume, volumes, analytics):
        """
        Calculate the analytics using the given fundamentals but only for the latest tick.

        Parameters
        ----------
        latest_volume : double
            The latest tick volume.
        fundamentals : double[]
            An array of fundamentals.
        analytics : double[]
            An array of analytics values.

        Returns
        -------
            An array of the calculated analytics.
        """

        z_score = stats.zscore([*volumes, latest_volume])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": latest_volume,
            "last_z_score": z_score,
        }
