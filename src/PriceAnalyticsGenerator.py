from datetime import datetime
import scipy.stats as stats


class PriceAnalyticsGenerator:
    """
    Represents a class that ... TODO

    ...

    Instance Attributes
    ----------
    __logger : Logger
        The logger of this class.
    """

    def generate(self, asset_data):
        """
        TODO

        Parameters
        ----------
        asset_data

        Returns
        -------

        """

        # TODO: Insert price data into SQL table
        return {
            datum["symbol"]: self.construct_price_record(datum)
            for datum in asset_data["data"]
        }

    def construct_price_record(self, entry):
        """
        TODO
        Returns
        -------

        """
        parse_time_series = lambda ts: [
            (
                datetime.fromtimestamp(entry["time"]).strftime("%Y-%m-%d, %H:%M:%S"),
                entry["close"],
            )
            for entry in ts
        ]

        time_series = parse_time_series(entry["timeSeries"])
        last_price = entry["price"]
        prices = [entry[1] for entry in time_series]
        prices.append(last_price)
        z_score = stats.zscore(prices)[-1]

        return {
            "time_series": time_series,
            "last_price": last_price,
            "z_score": z_score,
        }
