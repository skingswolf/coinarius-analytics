from threading import Thread
import time

from utils.logger import Logger


class AnalyticsEngineThread(Thread):
    """
    Represent the thread the analytics engine runs on

    ...

    Instance Attributes
    -------------------
    __socket_io : obj
        The SocketIO object
    __analytics_engine : obj
        The analytics engine
    __engine_thread_stop_event : obj
        The stop event for the engine thread.
    """

    def __init__(self, socket_io, analytics_engine, engine_thread_stop_event):
        """
        Initialises the engine thread.

        Parameters
        ----------
        socket_io : obj
            The SocketIO object
        analytics_engine : obj
            The analytics engine
        engine_thread_stop_event : obj
            The stop event for the engine thread.
        """

        super(AnalyticsEngineThread, self).__init__()

        self.__logger = Logger.get_instance()
        self.__socket_io = socket_io
        self.__analytics_engine = analytics_engine
        self.__engine_thread_stop_event = engine_thread_stop_event

    def run(self):
        """
        Runs the analytics engine thread.
        """

        self.__logger.log("Starting Analytics Engine Thread.")
        i = 1

        while not self.__engine_thread_stop_event.is_set():
            lag = self.__analytics_engine.update_lag
            self.__logger.log(
                f"Waiting {lag} seconds before updating analytics engine."
            )
            time.sleep(lag)

            self.__logger.log(f"Updating engine for the {i}th time.")
            analytics = self.__analytics_engine.update()

            self.__socket_io.emit("fresh_analytics", {"analytics": analytics})
            i += 1
