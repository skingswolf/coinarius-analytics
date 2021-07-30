import os
import requests

from logger import Logger


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
    __logger : Logger
        The logger of this class.
    __api_key : String
        The LunarCrush API key

    """

    symbols = "BTC,ETH,LTC"
    lunar_crush_base_url = "https://api.lunarcrush.com/v2"

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        self.__api_key = os.environ["LUNAR_CRUSH_API_KEY"]
        self.__logger = Logger.get_instance()

    def fetch_asset_data(self):
        """
        Fetches asset data such as close data, volumetric data, etc, from
        the LunarCrush API.

        Returns
        -------
            A dictionary where the keys are the asset symbols and the values asset data
            (e.g. time series data, etc).
        """
        self.__logger.log("Fetching asset data from the LunarCrush API.")

        query = {
            "data": "assets",
            "key": self.__api_key,
            "symbol": LunarCrushClient.symbols,
            "interval": "day",
            "time_series_indicators": "close",
            "data_points": 100,
        }
        response = requests.get(LunarCrushClient.lunar_crush_base_url, params=query)

        return response.json()


if __name__ == "__main__":
    lunar_crush_client = LunarCrushClient()
    lunar_crush_client.fetch_asset_data()
