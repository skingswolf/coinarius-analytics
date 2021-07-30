from datetime import datetime
import scipy.stats as stats
import time

from logger import Logger


class AnalyticsEngine:
    """
    Represents the engine that drives all the data fetching and the
    generation and delivery of analytics to web clients of Coinarius.

    ...

    Instance Attributes
    ----------
    __logger : Logger
        The logger of this class.
    __lunar_crush_client : LunarCrushClient
        The client for the LunarCrush API.
    """

    def __init__(self, lunar_crush_client):
        """
        Initialises a new instance of this class.
        """
        self.__logger = Logger.get_instance()
        self.__lunar_crush_client = lunar_crush_client
        self.__is_initialised = False

        self.price_data = None

    def initialise(self):
        """
        Initialises the analytics engine, fetching relevant data from the
        LunarCrush API required for starting the engine later

        Returns
        -------
        TODO
        """
        if self.__is_initialised:
            self.__logger.log(
                "Skipping the analytics engine initialisation as it has already been initialised!"
            )
            return

        self.__logger.log("Initialising analytics engine!")
        self.__is_initialised = True
        raw_asset_data = self.__lunar_crush_client.fetch_asset_data()

        # TODO: Insert price data

        price_data = self.generate_price_analytics(raw_asset_data)
        self.set_price_data(price_data)

    def start(self):
        """
        Starts the analytics engine, which runs a infinite loop that
        periodically polls the LunarCrushAPI for new data.

        Returns
        -------
        TODO
        """
        i = 0

        while True:
            i += 1
            time.sleep(2)
            self.__logger.log(f"{i}th iteration of the engine's infinite loop")

    def get_price_data(self):
        return self.__price_data

    def set_price_data(self, value):
        self.__price_data = value

    price_data = property(get_price_data, set_price_data)

    def generate_price_analytics(self, asset_data):
        """
        TODO
        Returns
        -------
        TODO
        """
        parse_time_series = lambda ts: [
            (
                datetime.fromtimestamp(entry["time"]).strftime("%Y-%m-%d, %H:%M:%S"),
                entry["close"],
            )
            for entry in ts
        ]

        def construct_price_record(datum):
            time_series = parse_time_series(datum["timeSeries"])
            last_price = datum["price"]
            prices = [entry[1] for entry in time_series]
            prices.append(last_price)
            z_score = stats.zscore(prices)[-1]

            return {
                "time_series": time_series,
                "last_price": last_price,
                "z_score": z_score,
            }

        return {
            datum["symbol"]: construct_price_record(datum)
            for datum in asset_data["data"]
        }
