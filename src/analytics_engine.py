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

        TODO
    """

    def __init__(self, lunar_crush_client, price_analytics_generator):
        """
        Initialises a new instance of this class.

        TODO
        """
        self.__logger = Logger.get_instance()
        self.__lunar_crush_client = lunar_crush_client
        self.__is_initialised = False
        self.__earliest_time = None
        self.__latest_time = None

        self.__price_analytics_generator = price_analytics_generator

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
        price_data = self.__price_analytics_generator.generate(raw_asset_data)

        raw_time_series = raw_asset_data["data"][0]["timeSeries"]
        self.__earliest_time = raw_time_series[0]["time"]
        self.__latest_time = raw_time_series[-1]["time"]

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
        update_lag = 15  # lag in seconds
        day_in_seconds = 24 * 60 * 60

        while True:
            i += 1
            time.sleep(update_lag)
            self.__logger.log(
                f"Polling LunarCrush API for the {i}th time to see if there's any fresh data"
            )

            current_time = datetime.timestamp(datetime.now())
            raw_asset_data = self.__lunar_crush_client.fetch_asset_data()

            if current_time - self.__latest_time < day_in_seconds:
                # Just find the most recent price and push update to websocket.
                latest_prices = {
                    datum["symbol"]: datum["price"] for datum in raw_asset_data["data"]
                }

                # TODO push to websocket connection.
                continue

            # TODO: Insert price data into SQL table
            # TODO push to websocket connection.
            price_data = self.__price_analytics_generator.generate(raw_asset_data)
            self.set_price_data(price_data)

    def get_price_data(self):
        return self.__price_data

    def set_price_data(self, value):
        self.__price_data = value

    price_data = property(get_price_data, set_price_data)
