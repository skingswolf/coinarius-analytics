from flask import Flask
from multiprocessing import Process

from calculators.price_calculator import PriceCalculator
from calculators.returns_calculator import ReturnsCalculator
from core.analytics_engine import AnalyticsEngine
from core.symbol_store import SymbolStore
from utils.logger import Logger
from network.lunar_crush_client import LunarCrushClient


logger = Logger.get_instance()

symbol_store = SymbolStore.get_instance()
lunar_crush_client = LunarCrushClient(symbol_store)

calculators = [PriceCalculator(), ReturnsCalculator()]
analytics_engine = AnalyticsEngine(lunar_crush_client, symbol_store, calculators)

app = Flask(__name__)


@app.route("/")
def index():
    logger.log("Handling request to root URI by returning price dataframe.")

    return analytics_engine.engine_output


if __name__ == "__main__":
    logger.log("Starting Coinarius Analytics!")
    analytics_engine.initialise()

    engine_process = Process(target=analytics_engine.run)
    engine_process.start()

    logger.log("Starting Flask server!")
    app.run(debug=True, use_reloader=False)

    engine_process.join()
