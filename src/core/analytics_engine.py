from datetime import datetime
import time

from utils.logger import Logger


class AnalyticsEngine:
    """
    Represents the engine that drives all the data fetching and the
    generation and delivery of analytics to web clients of Coinarius.

    ...

    Instance Attributes
    ----------
    _logger : Logger
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
        self.__price_analytics_generator = price_analytics_generator

        self.__is_initialised = False
        self.__earliest_time = None
        self.__latest_time = None
        self.__raw_asset_data = None
        self.__price_data = None

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

        self.__update_raw_asset_data()

        self.__price_data = self.__price_analytics_generator.calculate(
            self.__raw_asset_data
        )

        self.__is_initialised = True

    def run(self):
        """
        Starts running the analytics engine, which runs a infinite loop that
        periodically polls the LunarCrushAPI for new data.
        """

        if not self.__is_initialised:
            # TODO: throw an error
            return

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

            self.__update_raw_asset_data()

            if current_time - self.__latest_time < day_in_seconds:
                # Just find the most recent price and push update to websocket.
                latest_prices = {
                    datum["symbol"]: datum["price"]
                    for datum in self.__raw_asset_data["data"]
                }

                # TODO push lastest tick + historical changes to websocket connection.
                continue

            # TODO push historical changes to websocket connection.
            self.__price_data = self.__price_analytics_generator.calculate(
                self.__raw_asset_data
            )

    def __update_raw_asset_data(self):
        """
        Updates stale data in raw asset data cache with fresh data from the Lunar Crush API.
        """

        self.__logger.log(
            "Replacing stale data in raw asset data cache with fresh data from the API"
        )

        self.__raw_asset_data = self.__lunar_crush_client.fetch_asset_data()
        raw_time_series = self.__raw_asset_data["data"][0]["timeSeries"]
        self.__earliest_time = raw_time_series[0]["time"]
        self.__latest_time = raw_time_series[-1]["time"]

    @property
    def price_data(self):
        return self.__price_data
