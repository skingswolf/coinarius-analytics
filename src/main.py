from flask import Flask
from multiprocessing import Process

from calculators.price_calculator import PriceCalculator
from core.analytics_engine import AnalyticsEngine
from core.symbol_store import SymbolStore
from utils.logger import Logger
from network.lunar_crush_client import LunarCrushClient


logger = Logger.get_instance()

symbol_store = SymbolStore.get_instance()
lunar_crush_client = LunarCrushClient(symbol_store)
price_analytics_generator = PriceCalculator()
analytics_engine = AnalyticsEngine(
    lunar_crush_client, price_analytics_generator, symbol_store
)

app = Flask(__name__)


@app.route("/")
def index():
    logger.log("Handling request to root URI by returning price dataframe.")

    return analytics_engine.price_data


@app.before_first_request
def init_coinarius_analytics():
    logger.log("Initialising Coinarius Analytics engine for the foo'th time!")
    analytics_engine.initialise()


if __name__ == "__main__":
    logger.log("Starting Coinarius Analytics for the zee'th time!")
    analytics_engine.initialise()

    engine_process = Process(target=analytics_engine.run)
    engine_process.start()

    logger.log("Starting Flask server!")
    app.run(debug=True, use_reloader=False)

    engine_process.join()
