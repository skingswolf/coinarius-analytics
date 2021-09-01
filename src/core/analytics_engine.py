from datetime import datetime
import time

from utils.logger import Logger


class AnalyticsEngine:
    """
    Represents the engine that drives all the data fetching and the
    generation and delivery of analytics to web clients of Coinarius.

    ...

    Class Attributes
    ----------------
    update_lag : int
        The number of seconds between when the `update`
        method is called.

    Instance Attributes
    ----------
    _logger : Logger
        The logger of this class.
    __lunar_crush_client : LunarCrushClient
        The client for the LunarCrush API.
    symbol_store: SymbolStore
        The symbol store
    calculators: AnalyticsCalculators[]
        The list of analytics calculators.
    """

    update_lag = 60  # lag in seconds

    def __init__(self, lunar_crush_client, symbol_store, calculators):
        """
        Initialises a new instance of this class.

        Parameters
        ----------
        lunar_crush_client : LynarCryshClient
            The client for the LunarCrysh API

        """
        self.__logger = Logger.get_instance()
        self.__lunar_crush_client = lunar_crush_client
        self.__calculator_ids = [calculator.id for calculator in calculators]
        self.__fundamantals_calculators = [
            calculator for calculator in calculators if calculator.is_fundamental
        ]
        self.__calculators = {calculator.id: calculator for calculator in calculators}

        self.__symbol_store = symbol_store

        self.__is_initialised = False
        self.__earliest_time = None
        self.__latest_time = None
        self.__raw_asset_data = None
        self.analytics_data = {}
        self.engine_output = {}
        self.__last_update_time = None

    def initialise(self):
        """
        Initialises the analytics engine, fetching relevant data from the
        LunarCrush API required for starting the engine later

        """

        if self.__is_initialised:
            self.__logger.log(
                "Skipping the analytics engine initialisation as it has already been initialised!"
            )
            return

        self.__logger.log("Initialising analytics engine!")

        self.__update_raw_asset_data()

        self.__generate_analytics()

        self.__is_initialised = True

    def update(self):
        """
        Update increment in the analytics engine lifecycle, which is supposed to be run in a infinite loop that
        periodically polls the LunarCrushAPI for new data.
        """

        if not self.__is_initialised:
            self.__logger.log("Initialising engine before running the update method.")
            self.initialise()

        day_in_seconds = 24 * 60 * 60

        self.__logger.log("Polling LunarCrush API to see if there's any fresh data.")

        current_time = datetime.timestamp(datetime.now())
        is_next_day = current_time - self.__latest_time >= day_in_seconds

        num_datapoints = 5 if is_next_day else 100

        generate = (
            self.__generate_analytics
            if is_next_day
            else self.__generate_latest_analytics
        )
        self.__update_raw_asset_data(num_datapoints)

        self.__logger.log("Generating analytics for the requested update.")

        analytics = generate()
        self.__last_update_time = current_time

        return analytics

    def __generate_analytics(self):
        """
        Runs all calculators over the price data fetched from the LunarCrysh API, and then packages the
        results

        Returns
        -------
            A dictionary keyed by symbol containing all the generated anlaytics.
        """

        fundamentals_data = {
            calculator.id: calculator.calculate(self.__raw_asset_data)
            for calculator in self.__fundamantals_calculators
        }

        self.analytics_data = {
            calculator.id: fundamentals_data[calculator.id]
            if calculator.is_fundamental
            else calculator.calculate(fundamentals_data[f"{calculator.fundamental_id}"])
            for calculator in self.__calculators.values()
        }

        for symbol in self.__symbol_store.symbols:
            total_z_score = 0
            self.engine_output[symbol] = {}

            for calculator_id in self.__calculator_ids:
                self.engine_output[symbol][calculator_id] = self.analytics_data[
                    calculator_id
                ][symbol]

                total_z_score += abs(
                    self.engine_output[symbol][calculator_id]["last_z_score"]
                )

            self.engine_output[symbol]["name"] = self.__symbol_store.symbol_map[symbol]
            self.engine_output[symbol]["total_z_score"] = total_z_score

        return self.engine_output

    def __generate_latest_analytics(self):
        """
        Runs all calculators over the latest (tick) price data fetched from the LunarCrysh API, and then packages the
        results

        Returns
        -------
            A dictionary keyed by symbol containing all the generated anlaytics for the latest tick fundamentals.
        """

        fundamentals = [
            calculator.fundamental_id for calculator in self.__fundamantals_calculators
        ]

        latest_fundamentals = {
            datum["symbol"]: {
                fundamental: datum[fundamental] for fundamental in fundamentals
            }
            for datum in self.__raw_asset_data["data"]
        }

        # Get all the latest analytics, including
        # those from the price calculator
        latest_analytics = {
            calculator.id: calculator.calculate_latest(latest_fundamentals)
            for calculator in self.__calculators.values()
        }

        latest_engine_output = {
            symbol: {
                calculator_id: latest_analytics[calculator_id][symbol]
                for calculator_id in self.__calculator_ids
            }
            for symbol in self.__symbol_store.symbols
        }

        # Update the local cache for the engine output.
        # Calculate total z-score values for both the
        # engine output and latest engine output objects.
        for symbol in self.__symbol_store.symbols:
            total_z_score = 0

            for calculator_id in self.__calculator_ids:
                z_score = latest_engine_output[symbol][calculator_id][f"last_z_score"]

                self.engine_output[symbol][calculator_id][
                    f"last_{calculator_id}"
                ] = latest_engine_output[symbol][calculator_id][f"last_{calculator_id}"]
                self.engine_output[symbol][calculator_id]["last_z_score"] = z_score

                total_z_score += abs(z_score)

            self.engine_output[symbol]["total_z_score"] = total_z_score
            latest_engine_output[symbol]["total_z_score"] = total_z_score

        return latest_engine_output

    def __update_raw_asset_data(self, num_datapoints=100):
        """
        Updates stale data in raw asset data cache with fresh data from the Lunar Crush API.

        Parameters
        ----------
        num_datapoints : int
            The number of raw asset datapoints to fetch from the LunarCrush API.
        """

        self.__logger.log(
            "Replacing stale data in raw asset data cache with fresh data from the API"
        )

        self.__raw_asset_data = self.__lunar_crush_client.fetch_asset_data(
            num_datapoints
        )
        raw_time_series = self.__raw_asset_data["data"][0]["timeSeries"]
        self.__earliest_time = raw_time_series[0]["time"]
        self.__latest_time = raw_time_series[-1]["time"]
