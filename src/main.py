from flask import Flask
from multiprocessing import Process

from PriceAnalyticsGenerator import PriceAnalyticsGenerator
from analytics_engine import AnalyticsEngine
from logger import Logger
from lunar_crush_client import LunarCrushClient


logger = Logger.get_instance()

lunar_crush_client = LunarCrushClient()
price_analytics_generator = PriceAnalyticsGenerator()
analytics_engine = AnalyticsEngine(lunar_crush_client, price_analytics_generator)

app = Flask(__name__)


@app.route("/")
def index():
    logger.log("Handling request to root URI by returning price dataframe.")

    return analytics_engine.price_data


@app.before_first_request
def init_coinarius_analytics():
    logger.log("Initialising Coinarius Analytics engine!")
    analytics_engine.initialise()


if __name__ == "__main__":
    logger.log("Starting Coinarius Analytics!")
    analytics_engine.initialise()

    engine_process = Process(target=analytics_engine.start)
    engine_process.start()
    print("Bar")

    logger.log("Starting Flask server!")
    app.run(debug=True, use_reloader=False)

    engine_process.join()
