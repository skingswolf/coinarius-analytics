import logging
import os

import requests


class LunarCrushClient:
    """
    Represents a client to the LunarCrush API

    ...
    Class Attributes
    ----------
    api_key : String
        The LunarCrush API key
    lunar_crush_base_url : String
        Base URL for all calls to the LunarCrush API.

    Instance Attributes
    ----------
    __logger : Logger
        The logger of this class.

    """

    symbols = "BTC"

    # TODO: refactor this API key into an environment variable.
    api_key = "p9gd66qlvlkdvox9dltmnk"
    lunar_crush_base_url = "https://api.lunarcrush.com/v2"

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        self.__api_key = os.environ["LUNAR_CRUSH_API_KEY"]

    def fetch_asset_data(self):
        """
        Fetches asset data such as close data, volumetric data, etc, from
        the LunarCrush API.

        Returns
        -------
            A dictionary where the keys are the asset symbols and the values asset data
            (e.g. time series data, etc).
        """
        logging.info("Fetching asset data from the LunarCrush API.")

        query = {
            "data": "assets",
            "key": self.__api_key,
            "symbol": LunarCrushClient.symbols,
        }
        response = requests.get(LunarCrushClient.lunar_crush_base_url, params=query)

        return response.json()


if __name__ == "__main__":
    lunar_crush_client = LunarCrushClient()
    lunar_crush_client.fetch_asset_data()
