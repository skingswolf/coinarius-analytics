import os
import requests

from utils.logger import Logger


class LunarCrushClient:
    """
    Represents a client to the LunarCrush API

    ...
    Class Attributes
    ----------
    lunar_crush_base_url : String
        Base URL for all calls to the LunarCrush API.

    Instance Attributes
    ----------
    _logger : Logger
        The logger of this class.
    __api_key : String
        The LunarCrush API key
    __symbol_store
        The symbol store.
    """

    lunar_crush_base_url = "https://api.lunarcrush.com/v2"

    def __init__(self, symbol_store):
        """
        Initialises a new instance of this class.

        Parameters
        ----------
        symbol_store
            The symbol store.
        """

        self.__api_key = os.environ["LUNAR_CRUSH_API_KEY"]
        self.__logger = Logger.get_instance()
        self.__symbol_store = symbol_store

    def fetch_asset_data(self, num_of_datapoints=100):
        """
        Fetches asset data such as close data, volumetric data, etc, from
        the LunarCrush API.

        Parameters
        ----------
        num_of_datapoints : int
            The number of time series datapoints to fetch from the API.

        Returns
        -------
            A dictionary where the keys are the asset symbols and the values asset data
            (e.g. time series data, etc).
        """
        self.__logger.log("Fetching asset data from the LunarCrush API.")

        query = {
            "data": "assets",
            "key": self.__api_key,
            "symbol": str(self.__symbol_store),
            "interval": "day",
            "time_series_indicators": "close,volume",
            "data_points": num_of_datapoints,
        }
        response = requests.get(LunarCrushClient.lunar_crush_base_url, params=query)

        return response.json()


if __name__ == "__main__":
    lunar_crush_client = LunarCrushClient()
    lunar_crush_client.fetch_asset_data()
