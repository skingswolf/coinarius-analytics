import os

import psycopg2

from utils.logger import Logger


class DatabaseClient:
    """
    Represents client for managing connections to the
    nlp-analytics database.
    TODO: need to think about thread safety in this class.
    ...
    Attributes
    ----------
    __logger : Logger
        The logger of this class.
    __is_initialised : bool
        A boolean variable to keep track of whether the database client
        has been initialised or not.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        self.__logger = Logger.get_instance()
        self.__is_initialised = False
        self.__database_url = os.environ["DATABASE_URL"]
        self.__database_connection = None

    def initialise(self):
        """
        Initialises the device token manager.
        """
        if self.__is_initialised:
            self.__logger.log(
                "Skipping initialising the database client as it's already initialised."
            )
            return

        self.__logger.log("Initialising the database client.")
        try:
            self.__database_connection = psycopg2.connect(
                self.__database_url, sslmode="require"
            )
            self.__is_initialised = True
        except Exception as err:
            self.__logger.log(str(err))
            self.__logger.log("Failed to connect to the database.")

            raise err

    def execute_sql_query(self, query, handle_sql_result):
        """
        Executes the given SQL query.
        Parameters
        ----------
        query : str
            The SQL query.
        handle_sql_result : func
            A callback function to the handle the result of the SQL query
        Returns
        -------
            The result of calling `handle_result` on the sql query execution output.
        """
        if not self.__is_initialised:
            self.__logger.log(
                "Skipping executing the SQL query as the database client is not initialised."
            )

        cur = self.__database_connection.cursor()
        output = None

        try:
            cur.execute(query)

            output = handle_sql_result(cur, self.__database_connection)
        except Exception as err:
            # TODO: Throw an exception here.
            self.__logger.log(str(err))
            self.__logger.log("Failed to execute SQL query {}.".format(query))
            raise err
        finally:
            self.__logger.debug("Closing cursor of database connection.")
            cur.close()

        return output
