import logging


class AnalyticsEngine:
    """
    Represents the engine that drives all the data fetching and the
    generation and delivery of analytics to web clients of Coinarius.

    ...

    Attributes
    ----------
    __lunar_crush_client : LunarCrushClient
        The client for the LunarCrush API.
    """

    def __init__(self, lunar_crush_client):
        """
        Initialises a new instance of this class.
        """
        self.__logger = logging.getLogger("coinarius_analytics")
        self.__lunar_crush_client = lunar_crush_client

    def start(self):
        """
        Starts the analytics engine.

        Returns
        -------
        TODO
        """

        self.__logger.info("Starting analytics engine!")
        return self.__lunar_crush_client.fetch_asset_data()
